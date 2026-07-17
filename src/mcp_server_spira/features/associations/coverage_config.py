"""Coverage endpoint definitions per artifact type.

Key: artifact_type that supports coverage
Value: dict mapping dest_type → (endpoint_template, id_field_in_response)
"""

COVERAGE_MAP: dict[str, dict[str, tuple[str, str]]] = {
    "requirement": {
        "test_case": (
            "projects/{product_id}/requirements/{artifact_id}/test-cases",
            "TestCaseId",
        ),
        "test_step": (
            "projects/{product_id}/requirements/{artifact_id}/test-steps",
            "TestStepId",
        ),
    },
    "test_case": {
        "requirement": (
            "projects/{product_id}/test-cases/{artifact_id}/requirements",
            "RequirementId",
        ),
    },
    "release": {
        "test_case": (
            "projects/{product_id}/releases/{artifact_id}/test-cases",
            "TestCaseId",
        ),
    },
}
