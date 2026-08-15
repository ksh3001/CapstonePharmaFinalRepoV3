"""L0–L6 deterministic graders. Judge scoring is not a release gate."""

from __future__ import annotations

from typing import Any

from packages.contracts.deny import grade
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import SchemaError, validate
from packages.kernel.canonical import dumps
from packages.orchestrator.graph import DECLARED_STEPS


def l0_contract(pack: dict[str, Any], contract: str) -> dict[str, Any]:
    try:
        validate(pack, resolve_contract(contract))
        return {"level": "L0", "passed": True}
    except SchemaError as exc:
        return {"level": "L0", "passed": False, "reason": str(exc)}


def l1_deny_list(pack: dict[str, Any]) -> dict[str, Any]:
    hits = grade(pack)
    return {"level": "L1", "passed": not hits, "hits": hits}


def l2_no_converted_number(pack: dict[str, Any]) -> dict[str, Any]:
    rendered = dumps(pack).decode("utf-8")
    return {"level": "L2", "passed": "converted_value" not in rendered or '"converted_value":null' in rendered}


def l3_trajectory(steps: list[str] | tuple[str, ...]) -> dict[str, Any]:
    return {"level": "L3", "passed": tuple(steps) == DECLARED_STEPS}


def l4_subgroup_spread(spread: float, *, limit: float = 0.15) -> dict[str, Any]:
    return {"level": "L4", "passed": spread <= limit, "spread": spread, "limit": limit}


def l5_inject_refused(finding_present: bool) -> dict[str, Any]:
    return {"level": "L5", "passed": finding_present}


def l6_byte_identical(first: bytes, second: bytes, third: bytes) -> dict[str, Any]:
    return {"level": "L6", "passed": first == second == third}


def groundedness(advice: str, pack: dict[str, Any]) -> dict[str, Any]:
    from packages.advice.guards import guard_advice

    result = guard_advice(pack, {"text": advice, "evidence_refs": []})
    return {"level": "L6a", "passed": result.get("passed", False), "check": result.get("check")}
