"""Cross-cutting field projection utility.

Moved from ``features/search/tools/_shared.py`` — used by search tools
(mywork, product, program) and workspace tools.
"""

_DEFAULT_SCHEMA_HINT = "Use get_artifact_schema to discover valid fields."


def apply_field_projection(
    data: list[dict],
    fields: list[str] | None,
    summary_fields: list[str],
    all_fields: list[str],
    *,
    schema_hint: str | None = None,
) -> tuple[list[dict], list[str], list[str], list[str]]:
    """Project each object in *data* to a subset of fields.

    Returns ``(projected_data, fields_returned, fields_available, warnings)``.

    Spec:
        - ALWAYS returns a 4-tuple — never raises
        - fields=None or [] → uses summary_fields as the projection set
        - Explicit fields → intersected with all_fields; unknown names
          silently dropped with a warning listing them
        - ALL requested fields unknown → falls back to summary_fields with
          an additional warning
        - fields_returned = the actual field list used for projection
          (either summary_fields or the valid subset of requested fields)
        - fields_available = all_fields minus fields_returned; empty list
          when all fields are returned (not None, not omitted)
        - projected_data contains new dict objects (not mutated originals)
          with only keys in the valid field set
        - warnings is always a list (never None)
        - Order of fields_returned matches the order of the input fields
          list (or summary_fields order when defaulting)

    Behaviour:
    - *fields* is ``None`` or empty → use *summary_fields*.
    - Explicit *fields* → intersect with *all_fields*, drop unknowns with
      warning.
    - All requested fields unknown → fall back to *summary_fields* with
      warning.
    - ``fields_available`` is the delta (``all_fields - fields_returned``),
      or an empty list when all fields are returned.

    Parameters
    ----------
    schema_hint:
        Custom message appended to the unknown-fields warning.  When
        ``None``, falls back to the default artifact-schema hint for
        backward compatibility with existing search tools.
    """
    warnings: list[str] = []
    hint = schema_hint if schema_hint is not None else _DEFAULT_SCHEMA_HINT

    if not fields:
        # None or empty list → default to summary fields
        valid_fields = list(summary_fields)
    else:
        all_fields_set = set(all_fields)
        valid_fields = [f for f in fields if f in all_fields_set]
        unknown = [f for f in fields if f not in all_fields_set]

        if unknown:
            warnings.append(f"Unknown field(s) ignored: {', '.join(unknown)}. {hint}")

        if not valid_fields:
            warnings.append(
                "All requested fields are unknown. Falling back to default summary fields."
            )
            valid_fields = list(summary_fields)

    valid_set = set(valid_fields)
    projected = [{k: v for k, v in obj.items() if k in valid_set} for obj in data]

    fields_returned = valid_fields

    if set(valid_fields) == set(all_fields):
        fields_available: list[str] = []
    else:
        fields_available = [f for f in all_fields if f not in valid_set]

    return projected, fields_returned, fields_available, warnings
