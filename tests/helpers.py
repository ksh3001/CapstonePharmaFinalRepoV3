from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.config.paths import synthetic_dir
from scripts.build_fixture_copyset import build

CONTEXT = {
    "user": "participant_test_user",
    "purpose": "capstone_evaluation",
    "as_of": "2026-08-01T08:00:00Z",
    "execution": "disabled",
}


def ensure_copyset() -> Path:
    folder = synthetic_dir() / "evaluation" / "public_fixtures"
    if not folder.is_dir():
        build()
    return folder


def load_pub(name: str) -> dict[str, Any]:
    path = ensure_copyset() / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_with(
    evidence: list[dict[str, Any]],
    *,
    scenario_id: str = "SYN",
    workflow: str = "batch",
) -> dict[str, Any]:
    contracts = {
        "batch": "batch_response.schema.json",
        "pv": "pv_response.schema.json",
        "pv_intake": "pv_response.schema.json",
        "supply": "supply_response.schema.json",
        "supply_options": "supply_response.schema.json",
        "clinical": "advisory_nonexecuting",
        "regulatory": "advisory_nonexecuting",
        "integration": "advisory_nonexecuting",
        "privacy": "advisory_nonexecuting",
        "agent": "advisory_nonexecuting",
        "reliability": "advisory_nonexecuting",
        "security": "advisory_nonexecuting",
        "finops": "advisory_nonexecuting",
    }
    return {
        "scenario": {"id": scenario_id, "workflow": workflow},
        "authorized_context": dict(CONTEXT),
        "evidence": evidence,
        "response_contract": contracts.get(workflow, "batch_response.schema.json"),
    }


def walk_converted(obj: Any) -> list[str]:
    found: list[str] = []
    if isinstance(obj, dict):
        if obj.get("converted_value") not in (None, "", [], {}):
            found.append(str(obj.get("converted_value")))
        for value in obj.values():
            found.extend(walk_converted(value))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(walk_converted(item))
    return found
