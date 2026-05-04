"""Config dataclasses — single source of metadata per Spira entity type.

BaseFieldConfig: shared field-list attributes and validation.
ArtifactConfig:  metadata for artifact types (search, get, mywork tools).
WorkspaceConfig: metadata for workspace types (product, program, product_template).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BaseFieldConfig:
    """Shared base for ArtifactConfig and WorkspaceConfig.

    Holds the field-list attributes common to both config types
    and provides ``validate_fields()`` for consistency checks.
    """

    summary_fields: list[str]  # returned when fields=None/[]
    all_fields: list[str]  # LLM-visible fields from OpenAPI Remote* schema
    excluded_fields: list[str]  # OpenAPI fields hidden from LLM (guids, concurrency, etc.)

    def validate_fields(self) -> list[str]:
        """Validate field-list consistency. Returns error messages (empty = valid)."""
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

    def validate(self) -> list[str]:
        """Return list of error messages. Empty list means valid."""
        errors = self.validate_fields()
        if not self.sub_artifact_type:
            errors.append("sub_artifact_type is empty")
        if not self.endpoint_template:
            errors.append("endpoint_template is empty")
        if not self.parent_id_field:
            errors.append("parent_id_field is empty")
        if not self.openapi_schema:
            errors.append("openapi_schema is empty")
        return errors


@dataclass
class ArtifactConfig(BaseFieldConfig):
    """Holds all metadata for a single Spira artifact type.

    Used by unified tools to drive behaviour from configuration
    rather than per-artifact code.
    """

    artifact_type: str  # e.g. "incident"
    workspace_type: str  # "product" or "program"
    search_endpoint: str  # e.g. "projects/{product_id}/incidents/search"
    single_endpoint: str  # e.g. "projects/{product_id}/incidents/{artifact_id}"
    description: str  # for programmatic docstring generation

    # Normalised field mappings
    status_field: str | None
    owner_field: str | None
    priority_field: str | None
    release_field: str | None
    type_field: str | None

    supports_server_search: bool
    mywork_endpoint: str | None  # e.g. "incidents"

    # Query parameter names for the search endpoint (from OpenAPI spec).
    # Keys are logical roles, values are the actual API parameter names.
    # Varies per endpoint — incidents uses start_row/number_rows,
    # tasks uses starting_row/number_of_rows, etc.
    search_query_params: dict[str, str]

    # Sort defaults (activated in Spec G)
    default_sort_field: str | None
    default_sort_direction: str  # "asc" or "desc"

    # Sub-artifact includes (activated in Spec 13) — list of sub_artifact_type keys
    includes: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Return list of error messages. Empty list means valid."""
        errors: list[str] = self.validate_fields()
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
        """Return list of error messages. Empty list means valid."""
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
        """Return list of error messages. Empty list means valid."""
        errors: list[str] = self.validate_fields()
        if not self.workspace_type:
            errors.append("workspace_type is empty")
        if not self.description:
            errors.append("description is empty")
        if not self.list_endpoint:
            errors.append("list_endpoint is empty")
        return errors
