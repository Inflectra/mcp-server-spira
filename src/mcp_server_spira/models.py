"""Config dataclasses — single source of metadata per Spira entity type.

BaseFieldConfig:    shared field-list attributes and validation.
ArtifactConfig:     metadata for artifact types (search, get, mywork tools).
WorkspaceConfig:    metadata for workspace types (product, program, product_template).
FieldMeta:          type, description, and visibility for a single field.
Visibility:         enum controlling whether a field is shown to the LLM.
IncludableConfig:   protocol for any includable data type (sub-artifacts, comments).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class Visibility(Enum):
    """Controls how a field is exposed to the LLM.

    Every field in an artifact's OpenAPI schema falls into exactly one tier.
    The tiers are mutually exclusive and exhaustive.

    SUMMARY:  Returned by default when the LLM doesn't request specific fields.
              These are the most useful fields for quick identification
              (e.g. Name, Status, Owner). Always a subset of visible fields.

    VISIBLE:  Available to the LLM on request via the `fields` parameter,
              but not included in default responses. Keeps default output
              concise while allowing full access when needed.

    EXCLUDED: Exists in the API response but hidden from the LLM entirely.
              Used for internal/system fields (Guids, ConcurrencyDate,
              CustomProperties) that add noise without value for the LLM.
    """

    SUMMARY = "summary"
    VISIBLE = "visible"
    EXCLUDED = "excluded"


@dataclass(frozen=True, slots=True)
class FieldMeta:
    """Metadata for a single artifact field.

    Combines type information (for the schema tool), a human-readable
    description, and visibility control into one object. This is the
    single source of truth for field definitions — no separate lists needed.
    """

    type: str  # "int", "str", "bool", "datetime", "list"
    description: str
    visibility: Visibility = Visibility.VISIBLE


class IncludableConfig(Protocol):
    """Minimal interface for any includable data type.

    Both SubArtifactConfig and CommentConfig satisfy this protocol.
    The enrichment module dispatches uniformly against it.

    Uses @property declarations so that both mutable dataclass attributes
    (SubArtifactConfig) and frozen dataclass attributes (CommentConfig)
    satisfy the protocol. A @property in a Protocol means "readable" —
    both plain attributes and properties satisfy it.

    Spec:
        - Structural typing protocol — no inheritance required
        - summary_fields: fields returned by default (list[str])
        - all_fields: all LLM-visible fields (list[str])
        - post_filter: optional callable applied to raw API results
          before field projection; None means no filtering
    """

    @property
    def summary_fields(self) -> list[str]: ...

    @property
    def all_fields(self) -> list[str]: ...

    @property
    def post_filter(self) -> Callable[[list[dict]], list[dict]] | None: ...


@dataclass(frozen=True)
class IncludableEntry:
    """Registry entry for a flat-array includable type.

    Carries everything the enrichment loop needs to fetch, filter,
    project, and attach data — without knowing what kind of includable
    it is. Adding a new flat-array includable = one new registry entry,
    zero changes to the enrichment loop.

    Spec:
        - Frozen dataclass — immutable after construction at import time
        - config satisfies IncludableConfig protocol (field lists + post_filter)
        - endpoint_template contains {product_id} and {artifact_id} placeholders
        - id_field is the field name on the parent artifact dict that provides
          the artifact_id value for endpoint substitution
        - embedded_field (optional) is the raw field on the parent GET response
          that contains pre-fetched data, avoiding a redundant API call
    """

    config: IncludableConfig  # field lists + post_filter
    endpoint_template: str  # e.g. "projects/{product_id}/incidents/{artifact_id}/comments"
    id_field: str  # field on parent artifact providing artifact_id for endpoint
    embedded_field: str | None = None  # field on parent GET response to reuse


@dataclass
class BaseFieldConfig:
    """Shared base for ArtifactConfig and WorkspaceConfig.

    Holds the field-list attributes common to both config types
    and provides ``validate_fields()`` for consistency checks.

    WorkspaceConfig still uses the legacy list-based approach since
    workspace fields don't need type/description metadata.
    """

    summary_fields: list[str]  # returned when fields=None/[]
    all_fields: list[str]  # LLM-visible fields from OpenAPI Remote* schema
    excluded_fields: list[str]  # OpenAPI fields hidden from LLM (guids, concurrency, etc.)

    def validate_fields(self) -> list[str]:
        """Validate field-list consistency. Returns error messages (empty = valid).

        Spec:
        - ALWAYS returns a list[str], never raises — callers aggregate errors
          across many configs and raise a single ValueError at import time
        - Returns [] when all field-list invariants hold (valid config)
        - Checks four invariants: all_fields non-empty, summary_fields non-empty,
          summary_fields ⊆ all_fields, all_fields ∩ excluded_fields == ∅
        - Each violated invariant produces exactly one error message string
        - Error messages are human-readable and identify the offending field(s)
        - Pure function — no I/O, no side effects, no mutation of self
        """
        errors: list[str] = []
        if not self.all_fields:
            errors.append("all_fields is empty")
        if not self.summary_fields:
            errors.append("summary_fields is empty")
        for f in self.summary_fields:
            if f not in self.all_fields:
                errors.append(f"summary field '{f}' not in all_fields")
        overlap = set(self.all_fields) & set(self.excluded_fields)
        if overlap:
            errors.append(f"fields in both all_fields and excluded_fields: {sorted(overlap)}")
        return errors


@dataclass
class SubArtifactConfig(BaseFieldConfig):
    """Config for a sub-artifact type (test steps, mitigations, requirement steps)."""

    sub_artifact_type: str  # e.g. "test-steps"
    endpoint_template: str  # e.g. "projects/{product_id}/test-cases/{artifact_id}/test-steps"
    parent_id_field: str  # e.g. "TestCaseId" — field on parent providing artifact_id
    openapi_schema: str  # e.g. "RemoteTestStep" — for OpenAPI validation
    embedded_field: str = ""  # e.g. "TestSteps" — raw field on parent GET response to reuse

    # Creation support (None = sub-artifact does not support creation)
    create_endpoint: str | None = (
        None  # e.g. "projects/{product_id}/test-cases/{parent_id}/test-steps"
    )
    id_field: str | None = None  # e.g. "TestStepId"
    id_prefix: str | None = None  # e.g. "TS"
    required_fields: list[str] = field(default_factory=list)  # e.g. ["Description"]
    writable_fields: list[str] = field(default_factory=list)  # fields settable via POST

    # Update support (None = sub-artifact does not support update)
    single_endpoint: str | None = None  # GET URL for individual sub-artifact
    update_endpoint: str | None = None  # PUT URL template for sub-artifact

    # Post-filter applied to raw API results before field projection (IncludableConfig)
    post_filter: Callable[[list[dict]], list[dict]] | None = None

    def validate(self) -> list[str]:
        """Return list of error messages. Empty list means valid.

        Spec:
        - ALWAYS returns a list[str], never raises — callers aggregate errors
          across all sub-artifact configs and raise a single ValueError at import time
        - Returns [] when config is fully valid (field-list invariants + all
          required string fields non-empty + creation fields consistent +
          update fields consistent)
        - Delegates to validate_fields() first, then checks sub-artifact-specific
          required fields: sub_artifact_type, endpoint_template, parent_id_field,
          openapi_schema — each empty string produces exactly one error
        - If create_endpoint is set: id_field, id_prefix, required_fields
          must be non-empty; every entry in required_fields must appear in
          writable_fields — each violation produces exactly one error
        - If update_endpoint is set: single_endpoint must be non-empty,
          writable_fields must be non-empty — each violation produces one error
        - Error count for N empty string fields is exactly N (plus any
          validate_fields() errors) — tests assert precise error counts
        - Pure function — no I/O, no side effects, no mutation of self
        """
        errors = self.validate_fields()
        if not self.sub_artifact_type:
            errors.append("sub_artifact_type is empty")
        if not self.endpoint_template:
            errors.append("endpoint_template is empty")
        if not self.parent_id_field:
            errors.append("parent_id_field is empty")
        if not self.openapi_schema:
            errors.append("openapi_schema is empty")

        # Creation-specific validation: only checked when create_endpoint is set
        if self.create_endpoint is not None:
            if not self.id_field:
                errors.append("id_field is empty (required when create_endpoint is set)")
            if not self.id_prefix:
                errors.append("id_prefix is empty (required when create_endpoint is set)")
            if not self.required_fields:
                errors.append("required_fields is empty (required when create_endpoint is set)")
            for rf in self.required_fields:
                if rf not in self.writable_fields:
                    errors.append(f"required_field '{rf}' not in writable_fields")

        # Update-specific validation: only checked when update_endpoint is set
        if self.update_endpoint is not None:
            if not self.single_endpoint:
                errors.append("single_endpoint is empty (required when update_endpoint is set)")
            if not self.writable_fields:
                errors.append("writable_fields is empty (required when update_endpoint is set)")

        return errors


@dataclass
class ArtifactConfig:
    """Holds all metadata for a single Spira artifact type.

    Used by unified tools to drive behaviour from configuration
    rather than per-artifact code.

    Field definitions live in ``field_metadata`` — a single dict mapping
    field names to ``FieldMeta`` objects. The ``all_fields``,
    ``summary_fields``, and ``excluded_fields`` properties are derived
    from the Visibility enum on each FieldMeta. No duplication.
    """

    artifact_type: str  # e.g. "incident"
    workspace_type: str  # "product" or "program"
    search_endpoint: str  # e.g. "projects/{product_id}/incidents/search"
    single_endpoint: str  # e.g. "projects/{product_id}/incidents/{artifact_id}"
    description: str  # for programmatic docstring generation

    # The single source of truth for all fields on this artifact type.
    # Keys are field names, values carry type, description, and visibility.
    field_metadata: dict[str, FieldMeta]

    # Normalised field mappings (used by search filter resolution)
    status_field: str | None
    owner_field: str | None
    priority_field: str | None
    release_field: str | None
    type_field: str | None

    supports_server_search: bool
    mywork_endpoint: str | None  # e.g. "incidents"

    # Query parameter names for the search endpoint (from OpenAPI spec).
    search_query_params: dict[str, str]

    # Sort defaults
    default_sort_field: str | None
    default_sort_direction: str  # "asc" or "desc"

    # Sub-artifact includes — list of sub_artifact_type keys
    includes: list[str] = field(default_factory=list)

    # Comment support (None = type does not support comments)
    comments_endpoint: str | None = (
        None  # e.g. "projects/{product_id}/incidents/{artifact_id}/comments"
    )
    comments_body_is_array: bool = False  # Only incident uses array; all others use single object

    # Creation support (None = type does not support creation)
    create_endpoint: str | None = None  # e.g. "projects/{product_id}/incidents"
    id_field: str | None = None  # e.g. "IncidentId"
    id_prefix: str | None = None  # e.g. "IN"
    required_fields: list[str] = field(default_factory=list)
    inject_defaults: dict[str, int] = field(default_factory=dict)
    url_params: list[str] = field(default_factory=list)  # e.g. ["release_id"] for builds
    writable_fields: list[str] = field(default_factory=list)  # fields settable via POST

    # Update support (None = type does not support update)
    update_endpoint: str | None = None  # PUT URL template, e.g. "projects/{product_id}/tasks"

    # String-to-ID resolution: field_name → metadata section.
    # Used by field_resolver to resolve friendly names (e.g. "2 - High") to integer IDs
    # during create/update. Adding a new resolvable field = one entry here, zero structural
    # changes elsewhere. Sections must exist in metadata/api._SECTION_CONFIG_MAP.
    resolvable_fields: dict[str, str] = field(default_factory=dict)

    # --- Derived properties (computed from field_metadata) ---

    def build_search_url(
        self,
        *,
        starting_row: int = 1,
        number_of_rows: int = 100,
        release_id: int | str | None = None,
        **endpoint_kwargs: int,
    ) -> str:
        """Build the full search endpoint URL with config-driven query parameters.

        Spira WCF routing requires every parameter present in the URL for route
        matching, even when using default values.

        Spec:
            - Pure method — no I/O, no side effects, deterministic
            - Returns a URL string with query parameters appended
            - All search_query_params roles are represented in the URL
            - release_id query param is only included when release_id is not None
            - endpoint_kwargs are passed to search_endpoint.format() for
              placeholder substitution (product_id, program_id, release_id)
            - Never raises for any valid config

        Args:
            starting_row: 1-indexed start position for pagination.
            number_of_rows: Max results to return.
            release_id: Optional release ID (included as query param only when
                the config has a "release_id" role AND value is not None).
            **endpoint_kwargs: Substitution values for the endpoint template
                (e.g. product_id=55, program_id=3).
        """
        # Build format kwargs for endpoint template substitution
        format_kwargs: dict[str, int | str] = dict(endpoint_kwargs)
        if release_id is not None:
            format_kwargs.setdefault("release_id", release_id)

        endpoint = self.search_endpoint.format(**format_kwargs)

        query_parts: list[str] = []
        for role, api_name in self.search_query_params.items():
            if role == "row_start":
                query_parts.append(f"{api_name}={starting_row}")
            elif role == "row_count":
                query_parts.append(f"{api_name}={number_of_rows}")
            elif role in ("sort_field", "sort_by"):
                default = self.default_sort_field or ""
                query_parts.append(f"{api_name}={default}")
            elif role == "sort_direction":
                query_parts.append(f"{api_name}={self.default_sort_direction}")
            elif role == "release_id" and release_id is not None:
                query_parts.append(f"{api_name}={release_id}")
            elif role == "release_id":
                pass

        return f"{endpoint}?{'&'.join(query_parts)}"

    @property
    def summary_fields(self) -> list[str]:
        """Fields returned by default when the LLM doesn't specify `fields`."""
        return [
            name
            for name, meta in self.field_metadata.items()
            if meta.visibility == Visibility.SUMMARY
        ]

    @property
    def all_fields(self) -> list[str]:
        """All LLM-visible fields (summary + visible). Used by field projection."""
        return [
            name
            for name, meta in self.field_metadata.items()
            if meta.visibility in (Visibility.SUMMARY, Visibility.VISIBLE)
        ]

    @property
    def excluded_fields(self) -> list[str]:
        """Fields hidden from the LLM. Used by get response stripping."""
        return [
            name
            for name, meta in self.field_metadata.items()
            if meta.visibility == Visibility.EXCLUDED
        ]

    def validate(self) -> list[str]:
        """Return list of error messages. Empty list means valid.

        Spec:
        - ALWAYS returns a list[str], never raises — callers aggregate errors
          across all artifact configs and raise a single ValueError at import time
        - Returns [] when config is fully valid (all invariants hold)
        - Checks invariants in order:
          1. field_metadata must be non-empty
          2. Must have at least one SUMMARY field
          3. Must have at least one non-EXCLUDED field (all_fields non-empty)
          4. Required strings non-empty: artifact_type, workspace_type,
             search_endpoint, description
          5. workspace_type ∈ {"product", "program"}
          6. Normalised field mappings (status_field, owner_field, etc.):
             if non-None, must exist in all_fields
          7. search_query_params must be non-empty dict
          8. Each empty string in includes list produces exactly one error
          9. If create_endpoint is set: id_field, id_prefix, required_fields
             must be non-empty; every entry in required_fields must appear in
             writable_fields; every key in inject_defaults must appear in
             writable_fields
          10. If update_endpoint is set: writable_fields must be non-empty
        - Pure function — no I/O, no side effects, no mutation of self
        - Called at import time; failure prevents server startup
        """
        errors: list[str] = []

        # Field metadata validation
        if not self.field_metadata:
            errors.append("field_metadata is empty")
        if not self.summary_fields:
            errors.append("summary_fields is empty (no SUMMARY visibility fields)")
        if not self.all_fields:
            errors.append("all_fields is empty (no SUMMARY or VISIBLE fields)")

        if not self.artifact_type:
            errors.append("artifact_type is empty")
        if not self.workspace_type:
            errors.append("workspace_type is empty")
        if self.workspace_type not in ("product", "program"):
            errors.append(f"workspace_type '{self.workspace_type}' must be 'product' or 'program'")
        if not self.search_endpoint:
            errors.append("search_endpoint is empty")
        if not self.description:
            errors.append("description is empty")
        for attr in [
            "status_field",
            "owner_field",
            "priority_field",
            "release_field",
            "type_field",
        ]:
            val = getattr(self, attr)
            if val and val not in self.all_fields:
                errors.append(f"{attr} '{val}' not in all_fields")
        if not self.search_query_params:
            errors.append("search_query_params is empty")
        for inc in self.includes:
            if not inc:
                errors.append("includes contains an empty string")

        # Creation-specific validation
        if self.create_endpoint is not None:
            if not self.id_field:
                errors.append("id_field is empty (required when create_endpoint is set)")
            if not self.id_prefix:
                errors.append("id_prefix is empty (required when create_endpoint is set)")
            if not self.required_fields:
                errors.append("required_fields is empty (required when create_endpoint is set)")
            for rf in self.required_fields:
                if rf not in self.writable_fields:
                    errors.append(f"required_field '{rf}' not in writable_fields")
            for key in self.inject_defaults:
                if key not in self.writable_fields:
                    errors.append(f"inject_defaults key '{key}' not in writable_fields")

        # Update-specific validation
        if self.update_endpoint is not None and not self.writable_fields:
            errors.append("writable_fields is empty (required when update_endpoint is set)")

        return errors


@dataclass(frozen=True)
class TemplateMetadataFieldConfig:
    """Controls field projection and active filtering for a template metadata object.

    Works for types, priorities, statuses, severities, importances — any
    Remote* schema returned by project-templates/ endpoints.
    """

    active_field: str  # "IsActive" or "Active" — varies by schema
    id_field: str  # e.g. "RequirementTypeId", "PriorityId"
    endpoint: str  # e.g. "project-templates/{template_id}/requirements/types"
    include_fields: tuple[str, ...]  # fields to keep (beyond Name and id_field)
    excluded_fields: tuple[str, ...] = (  # fields always stripped
        "Guid",
        "ConcurrencyGuid",
        "LastUpdateDate",
    )

    def validate(self) -> list[str]:
        """Return list of error messages. Empty list means valid.

        Spec:
        - ALWAYS returns a list[str], never raises — callers aggregate errors
          across all template metadata configs and raise a single ValueError
          at import time
        - Returns [] when config is fully valid (all required fields non-empty)
        - Checks three required string fields: active_field, id_field, endpoint —
          each empty string produces exactly one error
        - Pure function — no I/O, no side effects, no mutation of self
        """
        errors: list[str] = []
        if not self.active_field:
            errors.append("active_field is empty")
        if not self.id_field:
            errors.append("id_field is empty")
        if not self.endpoint:
            errors.append("endpoint is empty")
        return errors


@dataclass
class WorkspaceConfig(BaseFieldConfig):
    """Config for a workspace type (product, program, product_template)."""

    workspace_type: str  # e.g. "product"
    description: str  # human-readable description
    list_endpoint: str  # e.g. "projects"
    single_endpoint: str | None  # e.g. "projects/{workspace_id}", None for program
    openapi_schema: str  # e.g. "RemoteProject"

    def validate(self) -> list[str]:
        """Return list of error messages. Empty list means valid.

        Spec:
        - ALWAYS returns a list[str], never raises — callers raise ValueError
          at import time if errors are non-empty
        - Returns [] when config is fully valid (field-list invariants +
          workspace-specific required fields non-empty)
        - Delegates to validate_fields() first (field-list invariants), then
          checks workspace-specific required strings: workspace_type,
          description, list_endpoint — each empty string produces exactly one error
        - Pure function — no I/O, no side effects, no mutation of self
        """
        errors: list[str] = self.validate_fields()
        if not self.workspace_type:
            errors.append("workspace_type is empty")
        if not self.description:
            errors.append("description is empty")
        if not self.list_endpoint:
            errors.append("list_endpoint is empty")
        return errors
