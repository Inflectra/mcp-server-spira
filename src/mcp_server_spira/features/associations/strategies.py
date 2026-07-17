"""Tier 2 enrichment strategies — associations and coverage.

These register at module import time into ENRICHMENT_STRATEGIES.
The enrichment loop dispatches to them without knowing their internals.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from mcp_server_spira.features.search.tools._include import (
    ENRICHMENT_STRATEGIES,
)

if TYPE_CHECKING:
    from mcp_server_spira.utils.spira_client import SpiraClient

logger = logging.getLogger(__name__)


async def _enrich_associations(
    spira_client: SpiraClient,
    product_id: int,
    artifacts: list[dict[str, Any]],
    artifact_type: str,
    warnings: list[str],
) -> None:
    """Tier 2 strategy: fetch associations, group by dest type, attach dict.

    Spec:
        - Looks up SPIRA_ARTIFACT_TYPE_IDS[artifact_type] for the numeric type ID
        - If artifact_type not in SPIRA_ARTIFACT_TYPE_IDS → warning + return
        - For each artifact, constructs endpoint:
          projects/{product_id}/associations/{type_id}/{artifact_id}
        - Fetches via await spira_client.make_spira_api_get_request(endpoint)
        - Calls _build_association_groups(raw) to get grouped dict + warnings
        - Attaches artifact["associations"] = grouped
        - Missing type_id → warning emitted, function returns early
        - API failure → {"total_count": 0} + warning
        - Empty response → {"total_count": 0}
        - All spira_client calls use await (async contract)
        - Never raises — all exceptions caught per-artifact
    """
    from mcp_server_spira.constants import SPIRA_ARTIFACT_TYPE_IDS
    from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
    from mcp_server_spira.features.associations.grouping import (
        _build_association_groups,
    )

    art_config = ARTIFACT_CONFIG.get(artifact_type)
    type_id = SPIRA_ARTIFACT_TYPE_IDS.get(artifact_type)
    if type_id is None or art_config is None:
        warnings.append(
            f"Artifact type '{artifact_type}' does not have a known "
            f"artifact_type_id for association retrieval."
        )
        return

    id_field_name = art_config.id_field
    if id_field_name is None:
        warnings.append(
            f"Artifact type '{artifact_type}' has no id_field configured for association retrieval."
        )
        return

    for artifact in artifacts:
        artifact_id = artifact.get(id_field_name)
        if artifact_id is None:
            artifact["associations"] = {"total_count": 0}
            continue

        endpoint = f"projects/{product_id}/associations/{type_id}/{artifact_id}"
        try:
            raw = await spira_client.make_spira_api_get_request(endpoint)
        except Exception as exc:
            artifact["associations"] = {"total_count": 0}
            warnings.append(f"Failed to fetch associations: {exc}")
            continue

        if not raw:
            artifact["associations"] = {"total_count": 0}
            continue

        grouped, group_warnings = _build_association_groups(raw)
        warnings.extend(group_warnings)
        artifact["associations"] = grouped


async def _enrich_coverage(
    spira_client: SpiraClient,
    product_id: int,
    artifacts: list[dict[str, Any]],
    artifact_type: str,
    warnings: list[str],
) -> None:
    """Tier 2 strategy: multi-endpoint fetch, merge into grouped dict.

    Spec:
        - Looks up COVERAGE_MAP[artifact_type] for endpoint definitions
        - If artifact_type not in COVERAGE_MAP → warning + return
        - For each artifact, iterates all coverage endpoints
        - Fetches each endpoint, extracts IDs from response items
        - Builds grouped result: {"total_count": N, "type": {"count": X, "ids": [...]}}
        - Attaches artifact["coverage"] = result
        - Unsupported type → warning emitted, function returns early
        - Partial failure (one endpoint fails) → that type omitted + warning
        - All endpoints fail → {"total_count": 0} + warnings
        - Empty results from endpoint → that type omitted from result
        - All spira_client calls use await (async contract)
        - Never raises — all exceptions caught per-endpoint
    """
    from mcp_server_spira.features.artifact_configs import ARTIFACT_CONFIG
    from mcp_server_spira.features.associations.coverage_config import (
        COVERAGE_MAP,
    )

    art_config = ARTIFACT_CONFIG.get(artifact_type)
    coverage_map = COVERAGE_MAP.get(artifact_type)
    if coverage_map is None or art_config is None:
        warnings.append(
            f"Artifact type '{artifact_type}' does not support coverage. "
            f"Valid types: requirement, test_case, release."
        )
        return

    id_field_name = art_config.id_field
    if id_field_name is None:
        warnings.append(
            f"Artifact type '{artifact_type}' has no id_field configured for coverage retrieval."
        )
        return

    for artifact in artifacts:
        artifact_id = artifact.get(id_field_name)
        if artifact_id is None:
            artifact["coverage"] = {"total_count": 0}
            continue

        result: dict[str, Any] = {"total_count": 0}
        for dest_type, (endpoint_template, id_field) in coverage_map.items():
            endpoint = endpoint_template.format(product_id=product_id, artifact_id=artifact_id)
            try:
                raw = await spira_client.make_spira_api_get_request(endpoint)
            except Exception as exc:
                warnings.append(f"Failed to fetch {dest_type} coverage: {exc}")
                continue
            if raw:
                ids = [item[id_field] for item in raw if id_field in item]
                if ids:
                    result[dest_type] = {"count": len(ids), "ids": ids}
                    result["total_count"] += len(ids)

        artifact["coverage"] = result


# Register at module import time — the enrichment loop picks them up.
ENRICHMENT_STRATEGIES["associations"] = _enrich_associations
ENRICHMENT_STRATEGIES["coverage"] = _enrich_coverage
