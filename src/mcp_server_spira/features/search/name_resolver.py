"""Name_Resolver — resolves display names to Spira integer IDs.

Async: resolves human-readable display names (e.g. "Open", "High", "Bug")
to Spira integer IDs for Tier 1 named filter parameters. Delegates fetching
and active-item filtering to the metadata feature's public API
(``features/metadata/api.py``). Requires a TemplateContext for shared
template_id caching across resolvers within one tool invocation.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
from mcp_server_spira.features.metadata.api import (
    fetch_active_metadata_items,
    get_id_field,
    get_state_config,
)
from mcp_server_spira.models import ArtifactConfig

if TYPE_CHECKING:
    from mcp_server_spira.features.search.template_context import TemplateContext
    from mcp_server_spira.utils.spira_client import SpiraClient

logger = logging.getLogger(__name__)

# Spira's /requirements/search always returns summary (parent) rows regardless
# of the status filter, and their rolled-up status may fall outside it. We
# surface this note instead of post-filtering (ADR-0008: no client-side filtering).
_REQUIREMENT_SUMMARY_FILTER_NOTE = (
    "Spira always returns summary (parent) requirements regardless of the status filter, "
    "so some returned rows may show a status outside the requested filter — those are "
    "summary requirements. Child requirements are filtered correctly."
)


class StateResolutionError(Exception):
    """A supported `state` filter could not be resolved into a trustworthy set.

    Raised by `resolve_state` when a *supported* artifact's lifecycle state
    cannot become a Tier 1 status-ID filter. Unsupported artifacts degrade to a
    warning (ADR-0002); a supported artifact whose state *is* the query must
    fail loudly rather than silently return unfiltered/empty results (ADR-0016).
    The product tool boundary maps it to the `STATE_UNRESOLVED` envelope; it is
    raised before `execute_search`, so no search POST is issued.

    Spec:
        - Raised only for supported metadata-driven kinds (incident, risk) that
          fail to resolve: missing Product Template ID; metadata fetch
          failure/warning; a non-boolean `Open` flag (missing, None, str, int,
          etc.); an empty or all-inactive status list; or an empty resolved
          open/closed partition.
        - Never for unsupported artifacts (they return a warning tuple).
        - Never for fixed artifacts (config-sourced tuples cannot fail at runtime).
    """


class NameResolver:
    """Resolves display names to Spira integer IDs with caching.

    Delegates fetching and active-item filtering to the metadata feature's
    public API; requires a TemplateContext for template_id resolution and
    artifact-kind mapping (shared cache across resolvers).

    All caches are instance-level, scoped to one tool invocation and shared
    across a fan-out's concurrent searches; ``_get_cached_items`` owns how
    concurrent misses coalesce into one fetch per key.
    """

    def __init__(
        self,
        spira_client: SpiraClient,
        template_context: TemplateContext,
    ) -> None:
        self._client = spira_client
        self._template_context = template_context
        # Keyed (template_id, metadata_section, artifact_kind, name_lower) → id.
        self._name_cache: dict[tuple[int, str, str, str], int] = {}
        # Keyed product_id → {name_lower: (component_id, original_name)}.
        self._component_cache: dict[int, dict[str, tuple[int, str]]] = {}
        self._current_user_id: int | None = None
        # Successful full active-item list, shared by status + state resolution
        # across the concurrent searches of one invocation.
        self._item_cache: dict[tuple[int, str, str], list[dict]] = {}
        # One lock per in-flight _item_cache key so concurrent callers coalesce
        # into a single fetch instead of racing.
        self._item_locks: dict[tuple[int, str, str], asyncio.Lock] = {}

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

        Delegates via the artifact-kind map to ``_resolve_name`` on the
        ``statuses`` section. Shared resolver contract: returns `(int, None)`
        or `(None, warning)`, never raises; integer-string bypass; active-only,
        case-insensitive match; successful resolutions cached.

        Spec:
            - Unknown artifact_type → `(None, warning)`.
            - Artifact kind not in STATUS_FIELD_CONFIGS → `(None, warning)`
              suggesting Tier 2 integer IDs.
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

    async def resolve_state(
        self,
        template_id: int | None,
        artifact_type: str,
        state: str,
    ) -> tuple[list[int] | None, str | None]:
        """Resolve a lifecycle `state` ("open"/"closed") to matching status IDs.

        Turns the two-value lifecycle abstraction over an artifact's statuses
        into one Tier 1 `RemoteFilter` `MultiValue` list on its status field.
        Config-driven: metadata-driven kinds (incident, risk) partition active
        statuses by the strict boolean `Open` flag; fixed kinds (requirement,
        task, test case) select a configured tuple with no metadata request.

        Spec:
            - Caller pre-normalizes `state` to lowercase "open"/"closed"; any
              other value raises `StateResolutionError`.
            - Success → `(non-empty ids, None)`, ready for exactly one status
              `MultiValue` entry.
            - `(None, warning)` only for an unsupported artifact (R6 unfiltered
              path); never for a supported one — the only non-raising failure.
            - Fixed artifacts resolve ONLY from `fixed_open_ids`/
              `fixed_closed_ids` (never one from the other), make zero API
              calls, accept `template_id is None`, and cannot raise (both tuples
              non-empty by import-time validation).
            - Metadata-driven kinds require a template_id; `None` raises.
            - Metadata-driven fetch goes through the shared per-key item cache
              (`_get_cached_items`): concurrent searches fetch once.
            - Partition with `type(flag) is bool` (True=open, False=closed); any
              non-bool / missing `Open` raises (never treated as closed).
            - Raise on fetch failure/warning, empty active list, all-inactive
              list, or an empty resolved partition for the requested side.
            - Unknown artifact types → warning tuple.

        Raises:
            StateResolutionError: see Spec (supported artifact, cannot resolve).
        """
        if state not in ("open", "closed"):
            # Caller must normalize/validate before branching here.
            raise StateResolutionError(f"State '{state}' is not normalized to 'open' or 'closed'.")

        artifact_kind = self._get_artifact_kind(artifact_type)
        if artifact_kind is None:
            return None, f"Unknown artifact type '{artifact_type}'."

        state_config = get_state_config(artifact_kind)
        if state_config is None:
            # Unsupported artifact (e.g. document, release): R6 warning path.
            return (
                None,
                f"'{artifact_type}' does not support state filtering. "
                "Search ran without a state filter.",
            )

        # --- Fixed/system-wide artifacts: explicit config tuples, zero I/O. ---
        if state_config.open_flag_field is None:
            ids = state_config.fixed_open_ids if state == "open" else state_config.fixed_closed_ids
            # Defensive: import-time validation already guarantees non-empty tuples.
            if not ids:
                raise StateResolutionError(
                    f"No fixed {state} status IDs configured for '{artifact_type}'."
                )
            return list(ids), None

        # --- Metadata-driven artifacts: strict boolean Open partition. ---
        if template_id is None:
            raise StateResolutionError(
                f"Cannot resolve state '{state}' for '{artifact_type}': "
                "no Product Template ID is available."
            )

        items, warning = await self._get_cached_items(template_id, "statuses", artifact_kind)
        if warning is not None or items is None:
            raise StateResolutionError(
                f"Cannot resolve state '{state}' for '{artifact_type}': "
                f"{warning or 'status metadata unavailable'}."
            )
        if not items:
            raise StateResolutionError(
                f"Cannot resolve state '{state}' for '{artifact_type}': "
                "no active statuses were found."
            )

        flag_field = state_config.open_flag_field
        id_field = state_config.id_field
        open_ids: list[int] = []
        closed_ids: list[int] = []
        for item in items:
            if flag_field not in item:
                raise StateResolutionError(
                    f"Active status is missing the '{flag_field}' flag while "
                    f"resolving state for '{artifact_type}'."
                )
            flag = item[flag_field]
            if type(flag) is not bool:
                raise StateResolutionError(
                    f"Active status has a non-boolean '{flag_field}' flag "
                    f"({flag!r}) while resolving state for '{artifact_type}'."
                )
            status_id = item.get(id_field)
            if not isinstance(status_id, int):
                raise StateResolutionError(
                    f"Active status is missing a valid '{id_field}' while "
                    f"resolving state for '{artifact_type}'."
                )
            if flag:
                open_ids.append(status_id)
            else:
                closed_ids.append(status_id)

        resolved = open_ids if state == "open" else closed_ids
        if not resolved:
            raise StateResolutionError(f"No {state} statuses resolved for '{artifact_type}'.")
        return resolved, None

    async def resolve_priority(
        self,
        template_id: int,
        artifact_type: str,
        display_name: str,
    ) -> tuple[int | None, str | None]:
        """Resolve a priority (or importance) display name to its integer ID.

        Shared resolver contract (see ``resolve_status``).

        Spec:
            - Requirement priority resolves transparently via its importance
              config — callers need not know the mapping.
            - Artifact kind not in PRIORITY_FIELD_CONFIGS (e.g. risk) →
              `(None, warning)` suggesting Tier 2.
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

        Shared resolver contract (see ``resolve_status``); inactive types are
        excluded from matching.

        Spec:
            - Artifact kind not in TYPE_FIELD_CONFIGS → `(None, warning)`.
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

        Shared resolver contract (see ``resolve_status``), with substring
        fallback; inactive severities excluded.

        Spec:
            - Artifact kind not in SEVERITY_FIELD_CONFIGS → `(None, warning)`
              suggesting Tier 2 integer IDs.
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

        Primary entry point for field_resolver's string-to-ID resolution;
        delegates to ``_resolve_name`` on *section* directly, so no per-category
        public method is needed. Shared resolver contract (see ``resolve_status``),
        with substring fallback.

        Spec:
            - Section/kind not in _SECTION_CONFIG_MAP → `(None, warning)`.
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

        The endpoint returns a single ``RemoteUser`` object (not an array).

        Spec:
            - `(int, None)` on success; cached, so a second call makes no API call.
            - `(None, warning)` on any failure (non-dict, missing UserId, API
              exception) — never raises; the warning always says "Owner filter
              skipped" so callers know it was not applied.
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

        The caller owns routing (builds use a URL path param;
        test_case/test_set use a query param); this method only resolves the
        value.

        Spec:
            - `(int, None)` on success; `(None, warning)` on any failure
              (empty results, no match, API exception) — never raises.
            - Integer-string bypass: "42" → `(42, None)` without API call.
            - Otherwise POSTs to release search and matches VersionNumber
              case-insensitively exact (the API's substring hits are filtered
              to exact); no match → warning listing versions found.
            - Search URL carries WCF routing query params (row_start/row_count/
              sort), required for Spira endpoint matching; POST body is a
              RemoteFilter array with VersionNumber StringValue.
        """
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

        # All query params are required for WCF endpoint routing.
        url = release_cfg.build_search_url(
            starting_row=1,
            number_of_rows=1,
            product_id=product_id,
        )

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

        target = release_value.lower()
        for entry in raw:
            version = entry.get("VersionNumber", "")
            if isinstance(version, str) and version.lower() == target:
                rid = entry.get("ReleaseId")
                if isinstance(rid, int):
                    return rid, None

        # The API's StringValue match is substring, so filter to exact above;
        # here list what was found.
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

        Returns ``(field_name, component_id, warning)``. The caller uses
        *field_name* to pick the filter format: ``ComponentIds`` → ``MultiValue``,
        ``ComponentId`` → ``IntValue``.

        Spec:
            - `(str, int, None)` on success; `(None, None, warning)` on any
              failure — never raises.
            - Field-name selection prefers "ComponentIds" over "ComponentId";
              neither present → warning "does not support component filtering".
            - Integer-string bypass: "10" → `(field_name, 10, None)` without API.
            - Active-only (IsActive=True) case-insensitive exact match;
              inactive components excluded from matching and from the warning's
              valid-names list.
            - No match → warning listing valid names sorted alphabetically;
              API failure → warning. Component list cached per product_id.
        """
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

        try:
            return field_name, int(component_value), None
        except (ValueError, TypeError):
            pass

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
        state: str | None = None,
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
            - ALWAYS returns `(filters, warnings)`, never raises, EXCEPT a
              supported-artifact `state` failure propagates `StateResolutionError`
              uncaught for the tool boundary to map to STATE_UNRESOLVED
              (ADR-0016); every other failure (incl. unsupported `state`, name
              miss) degrades to a warning.
            - First list: resolved `(field_name, value)` tuples for
              build_remote_filters. Second: warnings (always a list).
            - `state` → exactly ONE status-field `MultiValue` tuple
              `(config.status_field, list[int])`, not several ANDed entries;
              unsupported → warning + no filter; supported-unresolved → raise.
              `state`/`status` are mutually exclusive at the tool boundary.
            - A successfully applied `status` OR `state` filter on a REQUIREMENT
              search appends the summary-requirement note; NOT appended when the
              filter was skipped or unsupported.
            - Each param resolved independently (one failure doesn't block
              others); `None` value → skipped silently; `None` config field →
              warning + skip.
            - `template_id is None` → skip name resolution, attempt integer
              passthrough.
            - current_user takes precedence over owner_id (with a warning).
            - release_id here handles ONLY the server-side-filter case
              (non-build, non-query-param); caller owns URL query-param
              resolution.
            - requirement_id is a direct passthrough validated against
              config.all_fields.

        Args:
            template_id: Resolved template ID (None = skip name resolution).
            release_id: Release ID or version string — server-side filter only
                here (caller handles URL query params).

        Raises:
            StateResolutionError: propagated unchanged from `resolve_state`
                for a supported artifact (see Spec).
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
                    if artifact_type == "requirement":
                        warnings.append(_REQUIREMENT_SUMMARY_FILTER_NOTE)
            else:
                with contextlib.suppress(ValueError, TypeError):
                    tier1_filters.append((config.status_field, int(status)))
                    if artifact_type == "requirement":
                        warnings.append(_REQUIREMENT_SUMMARY_FILTER_NOTE)

        # --- State (lifecycle open/closed) ---
        # Unsupported artifacts warn; a supported-but-unresolvable one raises
        # StateResolutionError, propagating unchanged (ADR-0016) for the boundary.
        if state is not None:
            if config.status_field is None:
                warnings.append(f"'{artifact_type}' does not support state filtering.")
            else:
                resolved_ids, warning = await self.resolve_state(template_id, artifact_type, state)
                if warning:
                    warnings.append(warning)
                if resolved_ids is not None:
                    tier1_filters.append((config.status_field, resolved_ids))
                    if artifact_type == "requirement":
                        warnings.append(_REQUIREMENT_SUMMARY_FILTER_NOTE)

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
        # Only non-build types where release_id is NOT a URL query param; the
        # caller handles the query-param case (step 0b) separately.
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

    def _item_cache_lock(self, key: tuple[int, str, str]) -> asyncio.Lock:
        """Return the coordination lock for one item-cache key, creating it once.

        Spec:
            - Same `asyncio.Lock` per key, so concurrent callers for a missing
              key serialize on it and coalesce into a single fetch.
            - Lazily created on first request, retained for the resolver's
              lifetime (one tool invocation).
            - Pure/no-await, so lock creation itself can't interleave; never raises.
        """
        lock = self._item_locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._item_locks[key] = lock
        return lock

    async def _get_cached_items(
        self,
        template_id: int,
        section: str,
        artifact_kind: str,
    ) -> tuple[list[dict] | None, str | None]:
        """Fetch active metadata items for a key, caching and coalescing fetches.

        Shared backing fetch for status + state resolution, keyed
        `(template_id, section, artifact_kind)`. The single place that coalesces
        concurrent misses on one key into one API call.

        Spec:
            - `(items, None)` on success; the empty list is a valid, retained result.
            - `(None, warning)` on any fetch failure/warning — never raises
              (warning passed through from the metadata API).
            - Cache hit → zero API calls.
            - On a miss, the first caller takes the per-key lock and fetches;
              others await it and read the cached result → exactly one fetch per
              key per invocation.
            - Distinct keys fetch independently (N keys → N fetches).
            - Failures are NOT cached (key left absent so a retry re-fetches).
            - The lock bounds the only awaited work (event-loop safe).
        """
        key = (template_id, section, artifact_kind)
        cached = self._item_cache.get(key)
        if cached is not None:
            return cached, None

        async with self._item_cache_lock(key):
            # Double-checked: a caller we queued behind may have populated it.
            cached = self._item_cache.get(key)
            if cached is not None:
                return cached, None

            items, warning = await fetch_active_metadata_items(
                self._client, template_id, section, artifact_kind
            )
            if warning is not None:
                # Do not retain failures — leave the key absent so a retry re-fetches.
                return None, warning

            self._item_cache[key] = items
            return items, None

    async def _resolve_name(
        self,
        template_id: int,
        metadata_section: str,
        artifact_kind: str,
        display_name: str,
    ) -> tuple[int | None, list[str], str | None]:
        """Generic name resolution via the metadata feature's public API.

        Fetches active items via the shared item cache, then matches ``Name``
        case-insensitively (exact first, then substring fallback).

        Spec:
            - `(int, valid_names, None)` on match; `(None, valid_names, warning)`
              on no match (valid_names lists active names for the message);
              `(None, [], warning)` on infra failure (unknown section/kind, API
              error, empty response). Never raises.
            - Integer-string bypass: "42" → `(42, [], None)` without API call.
            - Cached by `(template_id, section, kind, name.lower())` — a repeat
              makes zero API calls.
            - Active-only candidates; exact match tried first.
            - Substring fallback (e.g. "high" matches "2 - High") succeeds only
              on a single match; multiple matches → ambiguity warning.
        """
        try:
            return int(display_name), [], None
        except (ValueError, TypeError):
            pass

        cache_key = (template_id, metadata_section, artifact_kind, display_name.lower())
        if cache_key in self._name_cache:
            return self._name_cache[cache_key], [], None

        # Shared, concurrency-safe item cache keyed (template_id, section, kind).
        filtered, warning = await self._get_cached_items(
            template_id, metadata_section, artifact_kind
        )
        if warning is not None or filtered is None:
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
            self._name_cache[cache_key] = matched_id
            return matched_id, valid_names, None

        # Substring fallback (e.g. "high" matches "2 - High"); only a single
        # match is accepted, to avoid ambiguity.
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
            - `{name_lower: (component_id, original_name)}` on success (empty if
              no active components); None only on API exception — never raises.
            - Active-only (IsActive=True).
            - Empty API response caches an empty dict (avoids retry); cached per
              product_id.
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
