"""CommentConfig — field definitions and filtering for comment includes.

One shared config instance for all artifact types. The per-type variation
is only the endpoint URL, which lives on ArtifactConfig.comments_endpoint.

Satisfies the IncludableConfig protocol so the enrichment module can
dispatch uniformly without type-specific branching.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from mcp_server_spira.models import FieldMeta, Visibility

# Short aliases for readability in field_metadata
S = Visibility.SUMMARY
E = Visibility.EXCLUDED


def _remove_deleted(comments: list[dict]) -> list[dict]:
    """Remove soft-deleted comments from raw API results.

    Spec:
        - Returns a new list containing only entries where
          IsDeleted is not True
        - Entries missing the IsDeleted key are retained
          (treated as not deleted)
        - Preserves relative order of retained entries
        - Pure function — no mutation of input list or dicts
    """
    return [c for c in comments if not c.get("IsDeleted", False)]


@dataclass(frozen=True)
class CommentConfig:
    """Config for comment include enrichment.

    Satisfies IncludableConfig protocol. One shared instance for all
    artifact types — the per-type variation is the endpoint URL on
    ArtifactConfig.comments_endpoint.

    Spec:
        - Frozen dataclass — immutable after creation
        - field_metadata is the single source of truth for field
          definitions; derived fields computed once in __post_init__
        - summary_fields: fields with Visibility.SUMMARY
        - all_fields: fields with SUMMARY or VISIBLE visibility
        - excluded_fields: fields with Visibility.EXCLUDED
        - post_filter: callable applied to raw API results before
          field projection; defaults to _remove_deleted
        - validate() returns error list (empty = valid), never raises
    """

    field_metadata: dict[str, FieldMeta]
    post_filter: Callable[[list[dict]], list[dict]] | None = _remove_deleted

    # Computed once at construction from field_metadata (not on every access).
    # Plain attributes satisfy the IncludableConfig protocol without type: ignore.
    summary_fields: list[str] = field(init=False)
    all_fields: list[str] = field(init=False)
    excluded_fields: list[str] = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "summary_fields",
            [
                name
                for name, meta in self.field_metadata.items()
                if meta.visibility == Visibility.SUMMARY
            ],
        )
        object.__setattr__(
            self,
            "all_fields",
            [
                name
                for name, meta in self.field_metadata.items()
                if meta.visibility in (Visibility.SUMMARY, Visibility.VISIBLE)
            ],
        )
        object.__setattr__(
            self,
            "excluded_fields",
            [
                name
                for name, meta in self.field_metadata.items()
                if meta.visibility == Visibility.EXCLUDED
            ],
        )

    def validate(self) -> list[str]:
        """Validate config consistency. Returns error messages.

        Spec:
            - ALWAYS returns a list[str], never raises
            - Returns [] when all invariants hold (valid config)
            - Checks: field_metadata non-empty, summary_fields
              non-empty, all_fields non-empty, summary_fields
              ⊆ all_fields, all_fields ∩ excluded_fields == ∅
            - Each violated invariant produces exactly one error
            - Pure function — no I/O, no side effects
        """
        errors: list[str] = []
        if not self.field_metadata:
            errors.append("field_metadata is empty")
        if not self.summary_fields:
            errors.append("summary_fields is empty")
        if not self.all_fields:
            errors.append("all_fields is empty")
        for f in self.summary_fields:
            if f not in self.all_fields:
                errors.append(f"summary field '{f}' not in all_fields")
        overlap = set(self.all_fields) & set(self.excluded_fields)
        if overlap:
            errors.append(f"fields in both all_fields and excluded_fields: {sorted(overlap)}")
        return errors


COMMENT_CONFIG = CommentConfig(
    field_metadata={
        # Summary fields — returned by default
        "UserName": FieldMeta("str", "Display name of the comment author", S),
        "Text": FieldMeta("str", "The comment body text", S),
        "CreationDate": FieldMeta("datetime", "When the comment was posted", S),
        # Excluded fields — present in API but hidden from LLM
        "CommentId": FieldMeta("int", "Unique comment identifier", E),
        "ArtifactId": FieldMeta("int", "Parent artifact ID", E),
        "Guid": FieldMeta("str", "Unique GUID", E),
        "UserId": FieldMeta("int", "Author user ID", E),
        "UserGuid": FieldMeta("str", "Author user GUID", E),
        "IsDeleted": FieldMeta("bool", "Whether comment is soft-deleted", E),
        "IsPermanent": FieldMeta("bool", "Whether comment is permanent", E),
    },
)

# Import-time validation — fail at startup, not runtime.
_errors = COMMENT_CONFIG.validate()
if _errors:
    raise ValueError("CommentConfig validation failed:\n" + "\n".join(_errors))
