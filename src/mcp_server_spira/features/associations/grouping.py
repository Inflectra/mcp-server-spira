"""Association grouping logic — pure data transformation, no I/O."""

from typing import Any

from mcp_server_spira.constants import SPIRA_ARTIFACT_TYPE_NAMES


def _build_association_groups(
    raw_associations: list[dict],
) -> tuple[dict[str, Any], list[str]]:
    """Transform raw RemoteAssociation list into grouped response shape.

    Spec:
        - Groups associations by DestArtifactTypeId → string name
        - Drops associations with unknown DestArtifactTypeId (not in
          SPIRA_ARTIFACT_TYPE_NAMES) with a warning per dropped item
        - Returns (grouped_dict, warnings)
        - grouped_dict has total_count + per-type count/artifacts
        - Each artifact entry: {"id": DestArtifactId, "name": DestArtifactName}
        - Empty input → ({"total_count": 0}, [])

    Returns:
        (grouped_dict, warnings). Associations with unknown
        DestArtifactTypeId are dropped with a warning.

    Output shape::

        {
            "total_count": 4,
            "test_case": {
                "count": 3,
                "artifacts": [{"id": 42, "name": "Login TC"}, ...]
            },
            "incident": {
                "count": 1,
                "artifacts": [{"id": 99, "name": "Crash"}]
            }
        }
    """
    groups: dict[str, list[dict[str, Any]]] = {}
    warnings: list[str] = []

    for assoc in raw_associations:
        dest_type_id: int | None = assoc.get("DestArtifactTypeId")
        if dest_type_id is None:
            warnings.append("Association to unknown artifact type ID None dropped.")
            continue

        dest_type_name = SPIRA_ARTIFACT_TYPE_NAMES.get(dest_type_id)
        if dest_type_name is None:
            warnings.append(f"Association to unknown artifact type ID {dest_type_id} dropped.")
            continue

        dest_id = assoc.get("DestArtifactId")
        dest_name = assoc.get("DestArtifactName", "")
        groups.setdefault(dest_type_name, []).append({"id": dest_id, "name": dest_name})

    result: dict[str, Any] = {"total_count": sum(len(v) for v in groups.values())}
    for type_name, artifacts in groups.items():
        result[type_name] = {
            "count": len(artifacts),
            "artifacts": artifacts,
        }

    return result, warnings
