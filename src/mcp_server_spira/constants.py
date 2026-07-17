"""Static Spira enum values. No runtime lookups needed."""

SPIRA_ARTIFACT_TYPE_IDS: dict[str, int] = {
    "requirement": 1,
    "test_case": 2,
    "incident": 3,
    "release": 4,
    "test_run": 5,
    "task": 6,
    "test_step": 7,
    "test_set": 8,
    "automation_host": 9,
    "automation_engine": 10,
    "requirement_step": 12,
    "document": 13,
    "risk": 14,
    "risk_mitigation": 15,
}

# Reverse mapping: numeric ID → our string name
SPIRA_ARTIFACT_TYPE_NAMES: dict[int, str] = {v: k for k, v in SPIRA_ARTIFACT_TYPE_IDS.items()}

# Association link types — only 1 and 2 are supported for creation
ARTIFACT_LINK_TYPE_IDS: dict[str, int] = {
    "related-to": 1,
    "depends-on": 2,
}

# Full registry (for reference / future use):
# 3=Implicit, 4=Source Code Commit, 5=Gantt: Finish-to-Start,
# 6=Gantt: Start-to-Start, 7=Gantt: Finish-to-Finish, 8=Gantt: Start-to-Finish

# Valid association pairs: source_type → set of allowed dest_types.
# From Spira documentation. Used to validate create_association requests.
# Note: test_set supports retrieval but not creation (no valid dest types).
VALID_ASSOCIATION_PAIRS: dict[str, frozenset[str]] = {
    "document": frozenset(
        {
            "requirement",
            "release",
            "test_case",
            "test_set",
            "test_run",
            "test_step",
            "automation_host",
            "task",
            "incident",
            "risk",
        }
    ),
    "incident": frozenset({"requirement", "test_step", "task", "incident", "risk"}),
    "release": frozenset({"release", "requirement"}),
    "requirement": frozenset({"release", "requirement", "incident", "risk"}),
    "risk": frozenset({"requirement", "incident", "risk", "test_case"}),
    "task": frozenset({"task", "incident"}),
    "test_case": frozenset({"task", "risk"}),
}

# Import-time consistency checks
assert len(SPIRA_ARTIFACT_TYPE_IDS) == len(SPIRA_ARTIFACT_TYPE_NAMES), (
    "Forward/reverse artifact type mappings are inconsistent"
)

# Validate all types in VALID_ASSOCIATION_PAIRS are known artifact types
_all_pair_types = set(VALID_ASSOCIATION_PAIRS.keys())
for _dests in VALID_ASSOCIATION_PAIRS.values():
    _all_pair_types.update(_dests)
_unknown = _all_pair_types - set(SPIRA_ARTIFACT_TYPE_IDS.keys())
assert not _unknown, f"VALID_ASSOCIATION_PAIRS references unknown types: {_unknown}"
