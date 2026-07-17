"""Name_Resolver — resolves display names to Spira integer IDs.

Async module that resolves human-readable display names (e.g. "Open",
"High", "Bug") to Spira integer IDs for Tier 1 named filter parameters.

Delegates to the metadata feature's public API
(``features/metadata/api.py``) for fetching and filtering active metadata
items. No direct imports of internal metadata configs or helpers.

Requires a TemplateContext for shared template_id caching across
resolvers within the same tool invocation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.metadata.api import (
    fetch_active_metadata_items,
    get_id_field,
)
from mcp_server_spira.models import ArtifactConfig

if TYPE_CHECKING:
    from mcp_server_spira.features.search.template_context import TemplateContext
    from mcp_server_spira.utils.spira_client import SpiraClient

logger = logging.getLogger(__name__)


class NameResolver:
    """Resolves display names to Spira integer IDs with caching.

    Delegates to the metadata feature's public API
    (fetch_active_metadata_items, get_id_field) for fetching and filtering
    active metadata items.

    Requires a TemplateContext for template_id resolution and
    artifact-kind mapping (shared cache across resolvers).

    All caches are instance-level, scoped to a single tool invocation.
    """

    def __init__(
        self,
        spira_client: SpiraClient,
        template_context: TemplateContext,
    ) -> None:
        self._client = spira_client
        self._template_context = template_context
        # Cache: (template_id, metadata_section, artifact_kind, name_lower) → int
        self._name_cache: dict[tuple[int, str, str, str], int] = {}
        # Cache: product_id → dict[name_lower, (component_id, original_name)]
        self._component_cache: dict[int, dict[str, tuple[int, str]]] = {}
        # Cache: current user ID (singleton)
        self._current_user_id: int | None = None

    async def get_template_id(self, product_id: int) -> int | None:
        """Fetch and cache ProjectTemplateId for a product.

        Delegates to TemplateContext (shared cache across resolvers).

        Spec:
            - Returns int on success, None on any failure — never raises
            - Caches per product_id — second call with same product_id
              makes zero API calls
            - Delegates entirely to TemplateContext (shared cache)
            - Non-dict response → None (graceful degradation)
            - Missing ProjectTemplateId key → None
            - Non-int ProjectTemplateId value → None
            - API exception → None (logged, not propagated)
        """
        return await self._template_context.get_template_id(product_id)

    # ------------------------------------------------------------------
    # Public resolvers — Tier 1 named parameters
    # ------------------------------------------------------------------

    async def resolve_status(
        self,
        template_id: int,
        artifact_type: str,
        display_name: str,
    ) -> tuple[int | None, str | None]:
        """Resolve a status display name to its integer ID.

        Maps *artifact_type* to the template metadata artifact kind via
        TemplateContext (or ``_ARTIFACT_KIND_MAP`` fallback), looks up the
        kind in ``STATUS_FIELD_CONFIGS``, and delegates to ``_resolve_name``.

        Spec:
            - Returns (int, None) on successful resolution
            - Returns (None, warning_string) on any failure — never raises
            - Unknown artifact_type (not in mapping) → (None,
              warning mentioning the artifact_type)
            - Artifact kind not in STATUS_FIELD_CONFIGS → (None, warning
              suggesting Tier 2 integer IDs)
            - Integer-string display_name (e.g. "42") → (42, None) without
              any API call — bypass path
            - Case-insensitive exact match on Name field of active items only
            - No match → (None, warning listing valid status names)
            - API failure → (None, warning suggesting integer ID fallback)
            - Successful resolution is cached — subsequent calls with same
              (template_id, artifact_type, display_name) skip the API

        Returns ``(id, warning)``.
        """
        artifact_kind = self._get_artifact_kind(artifact_type)
        if artifact_kind is None:
            return None, f"Unknown artifact type '{artifact_type}'."
        resolved_id, _valid, warning = await self._resolve_name(
            template_id,
            "statuses",
            artifact_kind,
            display_name,
        )
        return resolved_id, warning

    async def resolve_priority(
        self,
        template_id: int,
        artifact_type: str,
        display_name: str,
    ) -> tuple[int | None, str | None]:
        """Resolve a priority (or importance) display name to its integer ID.

        ``PRIORITY_FIELD_CONFIGS`` already maps Requirement → importance,
        so this method handles both priority and importance transparently.

        Spec:
            - Returns (int, None) on successful resolution
            - Returns (None, warning_string) on any failure — never raises
            - Unknown artifact_type → (None, warning)
            - Artifact kind not in PRIORITY_FIELD_CONFIGS (e.g. risk) →
              (None, warning suggesting Tier 2)
            - Integer-string bypass: "3" → (3, None) without API call
            - Requirement priority transparently resolves via importance
              config — callers don't need to know the mapping
            - Case-insensitive exact match on active items only

        Returns ``(id, warning)``.
        """
        artifact_kind = self._get_artifact_kind(artifact_type)
        if artifact_kind is None:
            return None, f"Unknown artifact type '{artifact_type}'."
        resolved_id, _valid, warning = await self._resolve_name(
            template_id,
            "priorities",
            artifact_kind,
            display_name,
        )
        return resolved_id, warning

    async def resolve_type(
        self,
        template_id: int,
        artifact_type: str,
        display_name: str,
    ) -> tuple[int | None, str | None]:
        """Resolve an artifact sub-type display name to its integer ID.

        Spec:
            - Returns (int, None) on successful resolution
            - Returns (None, warning_string) on any failure — never raises
            - Unknown artifact_type → (None, warning)
            - Artifact kind not in TYPE_FIELD_CONFIGS → (None, warning)
            - Integer-string bypass: "1" → (1, None) without API call
            - Inactive types are excluded from matching — only active items
              are candidates
            - Case-insensitive exact match

        Returns ``(id, warning)``.
        """
        artifact_kind = self._get_artifact_kind(artifact_type)
        if artifact_kind is None:
            return None, f"Unknown artifact type '{artifact_type}'."
        resolved_id, _valid, warning = await self._resolve_name(
            template_id,
            "types",
            artifact_kind,
            display_name,
        )
        return resolved_id, warning

    async def resolve_severity(
        self,
        template_id: int,
        artifact_type: str,
        display_name: str,
    ) -> tuple[int | None, str | None]:
        """Resolve a severity display name to its integer ID.

        Spec:
            - Returns (int, None) on successful resolution
            - Returns (None, warning_string) on any failure — never raises
            - Unknown artifact_type → (None, warning)
            - Artifact kind not in SEVERITY_FIELD_CONFIGS → (None, warning
              suggesting Tier 2 integer IDs)
            - Integer-string bypass: "1" → (1, None) without API call
            - Inactive severities are excluded from matching — only active
              items are candidates
            - Case-insensitive exact match, with substring fallback

        Returns ``(id, warning)``.
        """
        artifact_kind = self._get_artifact_kind(artifact_type)
        if artifact_kind is None:
            return None, f"Unknown artifact type '{artifact_type}'."
        resolved_id, _valid, warning = await self._resolve_name(
            template_id,
            "severities",
            artifact_kind,
            display_name,
        )
        return resolved_id, warning

    async def resolve_by_section(
        self,
        section: str,
        template_id: int,
        artifact_type: str,
        display_name: str,
    ) -> tuple[int | None, str | None]:
        """Generic resolution: resolve a display name via any metadata section.

        This is the primary entry point for field_resolver's string-to-ID
        resolution. It delegates to _resolve_name using the section directly,
        avoiding the need for one public method per metadata category.

        Spec:
            - Returns (int, None) on successful resolution
            - Returns (None, warning_string) on any failure — never raises
            - Unknown artifact_type → (None, warning)
            - Section/kind not in _SECTION_CONFIG_MAP → (None, warning)
            - Integer-string bypass handled by _resolve_name
            - Case-insensitive exact match with substring fallback

        Returns ``(id, warning)``.
        """
        artifact_kind = self._get_artifact_kind(artifact_type)
        if artifact_kind is None:
            return None, f"Unknown artifact type '{artifact_type}'."
        resolved_id, _valid, warning = await self._resolve_name(
            template_id,
            section,
            artifact_kind,
            display_name,
        )
        return resolved_id, warning

    async def resolve_current_user(
        self,
    ) -> tuple[int | None, str | None]:
        """Resolve the authenticated user's ID via ``GET /users``.

        The endpoint returns a single ``RemoteUser`` object (not an
        array).  The ``UserId`` is extracted and cached so subsequent
        calls skip the API round-trip.

        Spec:
            - Returns (int, None) on success
            - Returns (None, warning_string) on any failure — never raises
            - Caches the user ID — second call makes zero API calls
            - Non-dict response → (None, warning)
            - Missing UserId key → (None, warning)
            - API exception → (None, warning mentioning "Failed")
            - Warning always mentions "Owner filter skipped" so callers
              know the filter was not applied

        Returns ``(user_id, warning)``.
        """
        if self._current_user_id is not None:
            return self._current_user_id, None

        try:
            data = await self._client.make_spira_api_get_request(
                "users",
            )
        except Exception:
            logger.exception("Failed to fetch current user")
            return (
                None,
                "Failed to fetch current user. Owner filter skipped.",
            )

        if isinstance(data, dict):
            uid = data.get("UserId")
            if isinstance(uid, int):
                self._current_user_id = uid
                return uid, None

        return (
            None,
            "Could not extract UserId from current user response. Owner filter skipped.",
        )

    async def resolve_release(
        self,
        product_id: int,
        release_value: str,
        artifact_type: str,  # noqa: ARG002 — reserved for caller routing
    ) -> tuple[int | None, str | None]:
        """Resolve a release ID or version number to an integer ID.

        If *release_value* parses as an integer it is returned directly
        (bypass).  Otherwise a ``POST`` to the release search endpoint
        finds the matching ``ReleaseId`` by ``VersionNumber``.

        The caller is responsible for routing: builds keep release_id
        as a URL path param; test_case/test_set keep it as a URL query
        param.  This method only resolves the value.

        Spec:
            - Returns (int, None) on success
            - Returns (None, warning_string) on any failure — never raises
            - Integer-string bypass: "42" → (42, None) without API call
            - Version string search uses case-insensitive exact match on
              VersionNumber — substring matches from the API are filtered
              to exact matches
            - No exact match → (None, warning listing versions found)
            - Empty API results → (None, warning)
            - API exception → (None, warning mentioning "Failed")
            - Search URL includes WCF routing query params (row_start,
              row_count, sort params) — required for Spira endpoint matching
            - POST body is a RemoteFilter array with VersionNumber StringValue

        Returns ``(release_id, warning)``.
        """
        # Integer-string bypass
        try:
            return int(release_value), None
        except (ValueError, TypeError):
            pass

        release_cfg = ARTIFACT_CONFIG.get("release")
        if release_cfg is None:
            return (
                None,
                "Release config not found. Cannot resolve version number.",
            )

        # Build the search URL with ALL query params for WCF routing
        url = release_cfg.build_search_url(
            starting_row=1,
            number_of_rows=1,
            product_id=product_id,
        )

        # POST with VersionNumber filter
        filters = [
            {
                "PropertyName": "VersionNumber",
                "StringValue": release_value,
            },
        ]
        try:
            raw = await self._client.make_spira_api_post_request(
                url,
                filters,
            )
        except Exception:
            logger.exception(
                "Failed to search releases for product %d",
                product_id,
            )
            return (
                None,
                f"Failed to search releases in product {product_id}. Release filter skipped.",
            )

        if not raw or not isinstance(raw, list):
            return (
                None,
                f"No release matching version '{release_value}' found in product {product_id}.",
            )

        # Case-insensitive match on VersionNumber
        target = release_value.lower()
        for entry in raw:
            version = entry.get("VersionNumber", "")
            if isinstance(version, str) and version.lower() == target:
                rid = entry.get("ReleaseId")
                if isinstance(rid, int):
                    return rid, None

        # StringValue is a substring match — the API may return
        # results that don't exactly match.  List what was found.
        found = [e.get("VersionNumber", "?") for e in raw]
        return (
            None,
            f"No exact match for version "
            f"'{release_value}' in product {product_id}. "
            f"Versions found: {', '.join(found)}",
        )

    async def resolve_component(
        self,
        product_id: int,
        component_value: str,
        artifact_type: str,
        all_fields: list[str],
    ) -> tuple[str | None, int | None, str | None]:
        """Resolve a component name or ID for filtering.

        Returns ``(field_name, component_id, warning)`` where
        *field_name* is ``"ComponentId"`` or ``"ComponentIds"``
        depending on what the artifact's ``all_fields`` contains.

        If neither field is present the artifact type does not
        support component filtering and a warning is returned.

        The caller uses *field_name* to decide the filter format:
        ``ComponentIds`` → ``MultiValue``, ``ComponentId`` → ``IntValue``.

        Spec:
            - Returns (str, int, None) on success — never raises
            - Returns (None, None, warning_string) on any failure
            - Field name selection: "ComponentIds" preferred over
              "ComponentId" when both present in all_fields
            - Neither field in all_fields → (None, None, warning
              mentioning "does not support component filtering")
            - Integer-string bypass: "10" → (field_name, 10, None)
              without API call
            - Name matching is case-insensitive exact match on active
              components only (IsActive=True)
            - Inactive components are excluded from matching AND from
              the valid-names list in warnings
            - No match → (None, None, warning listing valid component
              names sorted alphabetically)
            - Component list is cached per product_id — subsequent calls
              for same product skip the API
            - API failure → (None, None, warning mentioning "Failed")
        """
        # Determine the correct field name from all_fields
        if "ComponentIds" in all_fields:
            field_name = "ComponentIds"
        elif "ComponentId" in all_fields:
            field_name = "ComponentId"
        else:
            return (
                None,
                None,
                f"'{artifact_type}' does not support component filtering.",
            )

        # Integer-string bypass
        try:
            return field_name, int(component_value), None
        except (ValueError, TypeError):
            pass

        # Fetch and cache component list
        comp_map = await self._get_components(product_id)
        if comp_map is None:
            return (
                None,
                None,
                f"Failed to fetch components for product {product_id}. Component filter skipped.",
            )

        target = component_value.lower()
        cid_entry = comp_map.get(target)
        if cid_entry is not None:
            cid, _original = cid_entry
            return field_name, cid, None

        valid = sorted(original for _, (_, original) in comp_map.items())
        return (
            None,
            None,
            f"'{component_value}' did not match any active "
            f"component in product {product_id}. "
            f"Valid components: {', '.join(valid)}",
        )

    # ------------------------------------------------------------------
    # Bulk resolution — replaces repetitive inline blocks in product.py
    # ------------------------------------------------------------------

    async def resolve_all_tier1(
        self,
        config: ArtifactConfig,
        product_id: int,
        template_id: int | None,
        *,
        artifact_type: str,
        status: str | None = None,
        priority: str | None = None,
        owner_id: int | None = None,
        current_user: bool = False,
        component: str | None = None,
        artifact_type_filter: str | None = None,
        release_id: int | str | None = None,
        requirement_id: int | None = None,
    ) -> tuple[list[tuple[str, int | list[int]]], list[str]]:
        """Resolve all Tier 1 named filter parameters into filter tuples.

        Encapsulates the repeated pattern: check config field → resolve via
        template metadata (or int passthrough) → accumulate warnings.

        Spec:
            - ALWAYS returns (list, list) — never raises
            - First list: resolved (field_name, value) tuples ready for
              build_remote_filters
            - Second list: accumulated warnings (always a list, never None)
            - Each named parameter is resolved independently — one failure
              does not block others
            - Parameters with None value are skipped (no warning, no filter)
            - Parameters whose config field is None produce a warning and
              are skipped
            - When template_id is None, name-based resolution is skipped
              and integer passthrough is attempted instead
            - current_user takes precedence over owner_id when both are
              provided (with a warning)
            - release_id resolution here handles ONLY the server-side filter
              case (non-build, non-query-param types) — URL query param
              resolution is the caller's responsibility
            - requirement_id is a direct passthrough (no name resolution) —
              validated against config.all_fields

        Args:
            config: ArtifactConfig for the artifact type being searched.
            product_id: Product ID (needed for component/release resolution).
            template_id: Resolved template ID (None = skip name resolution).
            artifact_type: Artifact type string (e.g. "incident").
            status: Display name or int string for status filter.
            priority: Display name or int string for priority filter.
            owner_id: Integer user ID for owner filter.
            current_user: If True, resolve authenticated user's ID.
            component: Component name or int string.
            artifact_type_filter: Sub-type display name or int string.
            release_id: Release ID (int) or version string for release filter.
                Only used as a server-side filter here — caller handles
                URL query param resolution separately.
            requirement_id: Integer requirement ID (direct passthrough).

        Returns:
            (tier1_filters, warnings)
        """
        import contextlib

        tier1_filters: list[tuple[str, int | list[int]]] = []
        warnings: list[str] = []

        # --- Status ---
        if status is not None:
            if config.status_field is None:
                warnings.append(f"'{artifact_type}' does not support status filtering.")
            elif template_id is not None:
                resolved_id, warning = await self.resolve_status(template_id, artifact_type, status)
                if warning:
                    warnings.append(warning)
                if resolved_id is not None:
                    tier1_filters.append((config.status_field, resolved_id))
            else:
                with contextlib.suppress(ValueError, TypeError):
                    tier1_filters.append((config.status_field, int(status)))

        # --- Priority ---
        if priority is not None:
            if config.priority_field is None:
                warnings.append(f"'{artifact_type}' does not support priority filtering.")
            elif template_id is not None:
                resolved_id, warning = await self.resolve_priority(
                    template_id, artifact_type, priority
                )
                if warning:
                    warnings.append(warning)
                if resolved_id is not None:
                    tier1_filters.append((config.priority_field, resolved_id))
            else:
                with contextlib.suppress(ValueError, TypeError):
                    tier1_filters.append((config.priority_field, int(priority)))

        # --- Owner (current_user / owner_id) ---
        if current_user and owner_id is not None:
            warnings.append(
                "Both 'owner_id' and 'current_user' provided. Using current_user; owner_id ignored."
            )
        if current_user:
            if config.owner_field is None:
                warnings.append(f"'{artifact_type}' does not support owner filtering.")
            else:
                uid, warning = await self.resolve_current_user()
                if warning:
                    warnings.append(warning)
                if uid is not None:
                    tier1_filters.append((config.owner_field, uid))
        elif owner_id is not None:
            if config.owner_field is None:
                warnings.append(f"'{artifact_type}' does not support owner filtering.")
            else:
                tier1_filters.append((config.owner_field, owner_id))

        # --- Component ---
        if component is not None:
            field_name, comp_id, warning = await self.resolve_component(
                product_id, str(component), artifact_type, config.all_fields
            )
            if warning:
                warnings.append(warning)
            if field_name is not None and comp_id is not None:
                if field_name == "ComponentIds":
                    tier1_filters.append((field_name, [comp_id]))
                else:
                    tier1_filters.append((field_name, comp_id))

        # --- Artifact type filter (sub-type) ---
        if artifact_type_filter is not None:
            if config.type_field is None:
                warnings.append(f"'{artifact_type}' does not support type filtering.")
            elif template_id is not None:
                resolved_id, warning = await self.resolve_type(
                    template_id, artifact_type, artifact_type_filter
                )
                if warning:
                    warnings.append(warning)
                if resolved_id is not None:
                    tier1_filters.append((config.type_field, resolved_id))
            else:
                with contextlib.suppress(ValueError, TypeError):
                    tier1_filters.append((config.type_field, int(artifact_type_filter)))

        # --- Requirement ID (direct passthrough) ---
        if requirement_id is not None:
            if "RequirementId" in config.all_fields:
                tier1_filters.append(("RequirementId", requirement_id))
            else:
                warnings.append(
                    f"'{artifact_type}' does not support requirement_id filtering "
                    "(RequirementId not in available fields). Filter ignored."
                )

        # --- Release ID as server-side filter ---
        # Only applies for non-build types where release_id is NOT a URL query param.
        # The caller handles URL query param resolution (step 0b) separately.
        if (
            release_id is not None
            and artifact_type != "build"
            and "release_id" not in config.search_query_params
        ):
            if isinstance(release_id, int):
                if config.release_field is not None:
                    tier1_filters.append((config.release_field, release_id))
                else:
                    warnings.append(
                        f"'{artifact_type}' does not support release filtering. Filter ignored."
                    )
            elif isinstance(release_id, str):
                resolved_rid, warning = await self.resolve_release(
                    product_id, release_id, artifact_type
                )
                if warning:
                    warnings.append(warning)
                if resolved_rid is not None:
                    if config.release_field is not None:
                        tier1_filters.append((config.release_field, resolved_rid))
                    else:
                        warnings.append(
                            f"'{artifact_type}' does not support release filtering. Filter ignored."
                        )

        return tier1_filters, warnings

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_artifact_kind(self, artifact_type: str) -> str | None:
        """Resolve artifact_type to metadata artifact kind string.

        Delegates to TemplateContext for the canonical mapping.

        Spec:
            - Pure lookup — no I/O, no side effects
            - Returns None for unknown artifact types
        """
        return self._template_context.get_metadata_artifact_kind(artifact_type)

    async def _resolve_name(
        self,
        template_id: int,
        metadata_section: str,
        artifact_kind: str,
        display_name: str,
    ) -> tuple[int | None, list[str], str | None]:
        """Generic name resolution via the metadata feature's public API.

        Delegates fetching and active-item filtering to
        ``fetch_active_metadata_items``, then does case-insensitive exact
        match (with substring fallback) on ``Name``.

        Spec:
            - Returns (int, valid_names, None) on successful match
            - Returns (None, valid_names, warning) on no match — valid_names
              lists all active item names for the caller/warning message
            - Returns (None, [], warning) on infrastructure failure (unknown
              section, unknown kind, API error, empty response)
            - Integer-string bypass: "42" → (42, [], None) without API call
            - Successful resolution is cached by (template_id,
              metadata_section, artifact_kind, display_name.lower()) — second
              call with same key makes zero API calls
            - Only active items (filtered by the metadata API) are
              candidates for matching — inactive items are invisible
            - Case-insensitive exact match on "Name" field is tried first
            - Substring fallback: if exact match fails, tries case-insensitive
              substring match (e.g. "high" matches "2 - High")
            - Substring match succeeds only when exactly one item matches —
              multiple substring matches produce an ambiguity warning
            - Never raises — all exceptions caught and converted to warning

        Args:
            template_id: Product template numeric ID.
            metadata_section: One of ``"statuses"``, ``"priorities"``,
                ``"types"``.
            artifact_kind: Template metadata artifact kind string
                (e.g. ``"Incident"``, ``"Test Case"``).
            display_name: The human-readable name to resolve.

        Returns:
            ``(id, valid_names, warning)`` — resolved ID (or None),
            list of valid display names, and an optional warning.
        """
        # Integer-string bypass
        try:
            return int(display_name), [], None
        except (ValueError, TypeError):
            pass

        # Check name cache
        cache_key = (template_id, metadata_section, artifact_kind, display_name.lower())
        if cache_key in self._name_cache:
            return self._name_cache[cache_key], [], None

        # Fetch active metadata items via the metadata feature's public API
        filtered, warning = await fetch_active_metadata_items(
            self._client, template_id, metadata_section, artifact_kind
        )
        if warning is not None:
            return None, [], warning

        # Get the ID field name for this section/kind
        id_field = get_id_field(metadata_section, artifact_kind)
        if id_field is None:
            return None, [], f"Unknown metadata section '{metadata_section}'."

        # Extract valid names and attempt case-insensitive exact match
        valid_names: list[str] = []
        name_lower = display_name.lower()
        matched_id: int | None = None

        for item in filtered:
            item_name = item.get("Name", "")
            valid_names.append(item_name)
            if item_name.lower() == name_lower:
                matched_id = item.get(id_field)

        if matched_id is not None:
            # Cache the successful resolution
            self._name_cache[cache_key] = matched_id
            return matched_id, valid_names, None

        # Fallback: case-insensitive substring match.
        # If the user provides "high" and the valid name is "2 - High",
        # we match because "high" is contained in "2 - high".
        # Only succeeds when exactly one item matches to avoid ambiguity.
        substring_matches: list[tuple[str, int]] = []
        for item in filtered:
            item_name = item.get("Name", "")
            if name_lower in item_name.lower():
                item_id = item.get(id_field)
                if isinstance(item_id, int):
                    substring_matches.append((item_name, item_id))

        if len(substring_matches) == 1:
            matched_name, matched_id = substring_matches[0]
            self._name_cache[cache_key] = matched_id
            return matched_id, valid_names, None

        if len(substring_matches) > 1:
            ambiguous = ", ".join(name for name, _ in substring_matches)
            return (
                None,
                valid_names,
                (
                    f"'{display_name}' is ambiguous for {artifact_kind} "
                    f"{metadata_section} — matches: {ambiguous}. "
                    f"Use a more specific name or integer ID."
                ),
            )

        # No match found (neither exact nor substring)
        names_list = ", ".join(sorted(valid_names))
        return (
            None,
            valid_names,
            (
                f"'{display_name}' did not match any {metadata_section} for "
                f"{artifact_kind}. Valid names: {names_list}"
            ),
        )

    async def _get_components(
        self,
        product_id: int,
    ) -> dict[str, tuple[int, str]] | None:
        """Fetch and cache active components for a product.

        Spec:
            - Returns dict on success (may be empty if no active components)
            - Returns None only on API exception — never raises
            - Dict keys are lowercased component names; values are
              (component_id, original_name) tuples
            - Only active components (IsActive=True) are included
            - Empty API response → caches empty dict (avoids retry on next
              call) and returns it
            - Cached per product_id — subsequent calls skip the API

        Returns a ``{name_lower: (component_id, original_name)}``
        dict of active components, or ``None`` on API failure.
        """
        if product_id in self._component_cache:
            return self._component_cache[product_id]

        try:
            raw = await self._client.make_spira_api_get_request(
                f"projects/{product_id}/components?active_only=true&include_deleted=false",
            )
        except Exception:
            logger.exception(
                "Failed to fetch components for product %d",
                product_id,
            )
            return None

        if not raw or not isinstance(raw, list):
            # No components — cache empty dict so we don't retry
            self._component_cache[product_id] = {}
            return self._component_cache[product_id]

        comp_map: dict[str, tuple[int, str]] = {}
        for item in raw:
            if not item.get("IsActive", False):
                continue
            name = item.get("Name", "")
            cid = item.get("ComponentId")
            if name and isinstance(cid, int):
                comp_map[name.lower()] = (cid, name)

        self._component_cache[product_id] = comp_map
        return comp_map
