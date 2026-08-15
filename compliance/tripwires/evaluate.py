"""Executable EU AI Act / ISO 42001 tripwires from the control map."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from packages.config.paths import repo_root
from packages.contracts.deny import DenyListError, assert_baseline
from packages.orchestrator.graph import DECLARED_STEPS, WORKFLOW_AGENTS

CLAIM = "EU AI Act applicability claim invalidated — re-run artefact 19"
FLOATING = frozenset({"latest", "current", "alias"})
REQUIRED_COLUMNS = ("obligation_id", "framework", "obligation", "control", "module", "test_id", "evidence_path", "status")
PROTECTED = (
    "packages/contracts/deny_list.json",
    "packages/contracts/deny_list.baseline.json",
    "evals/thresholds.yaml",
    "evals/thresholds.baseline.yaml",
    "evals/graders/deterministic/groundedness.py",
    "packages/advice/brief.py",
    "services/integration/mcp/tools.py",
    "services/integration/azure/openai.py",
)


def _root() -> Path:
    return repo_root()


def _read(rel: str) -> str:
    return (_root() / rel).read_text(encoding="utf-8")


def _load_json(rel: str) -> dict[str, Any]:
    return json.loads(_read(rel))


def file_sha256(rel: str) -> str:
    data = (_root() / rel).read_bytes()
    return hashlib.sha256(data).hexdigest()


def control_map() -> list[dict[str, str]]:
    path = _root() / "compliance" / "control-map.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _test_path(test_id: str) -> Path:
    rel = test_id.replace(".", "/") + ".py"
    return _root() / rel


def _parse_simple_yaml(rel: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in _read(rel).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def _trip(name: str, ok: bool, detail: str) -> dict[str, object]:
    return {"id": name, "ok": ok, "detail": detail if ok else f"{CLAIM}: {detail}"}


def trip_write_tools() -> dict[str, object]:
    from services.api.handlers import MUTATION_PATHS, inventory
    from services.integration.mcp.tools import TOOLS, tool_is_read_only

    dirty = [
        str(item.get("name") or "")
        for item in TOOLS
        if not tool_is_read_only(str(item.get("name") or ""), str(item.get("description") or ""))
    ]
    mutations = list(inventory()["mutations"])
    extra = [item for item in mutations if "acknowledge" not in item and "contest" not in item]
    if dirty or extra or len(MUTATION_PATHS) != 2:
        return _trip("write-tools", False, f"mutating capability present tools={dirty} mutations={mutations}")
    return _trip("write-tools", True, "MCP tools are read-only; mutations are acknowledge and contest")


def trip_human_review() -> dict[str, object]:
    from services.api.pack_view import render_pack_body

    if "approve" not in DECLARED_STEPS:
        return _trip("human-review", False, "approve step missing from DECLARED_STEPS")
    agents = _load_json("packages/config/agents.yaml")
    interrupts = (agents.get("agents") or {}).get("AG-1", {}).get("interrupts") or []
    if "approve" not in interrupts:
        return _trip("human-review", False, "AG-1 no longer raises the approve interrupt")
    for workflow in ("batch", "pv", "supply"):
        if workflow not in WORKFLOW_AGENTS:
            return _trip("human-review", False, f"workflow {workflow} has no declared agent")
    html = render_pack_body(
        {
            "evidence": [],
            "findings": [],
            "gaps": [],
            "abstentions": [],
            "contradictions": [],
            "human_review": {},
            "request_id": "REQ-tripwire",
        },
        title="Tripwire",
    ).casefold()
    if "acknowledgement" not in html and "/acknowledge" not in html:
        return _trip("human-review", False, "acknowledgement gate removed from the pack view")
    console = _read("services/api/console.py")
    handlers = _read("services/api/handlers.py")
    if "/contest" not in console or "/contest" not in handlers:
        return _trip("human-review", False, "contestability removed from console or API")
    return _trip("human-review", True, "approve interrupt and acknowledge/contest controls present")


def trip_model_pin() -> dict[str, object]:
    registry = _load_json("compliance/eu-ai-act/model-registry.json")
    forbidden = {item.casefold() for item in registry.get("forbidden_aliases") or FLOATING}
    allowed = {str(item) for item in (registry.get("pinned_versions") or []) + (registry.get("pinned_deployments") or [])}
    version = os.environ.get("AZURE_OPENAI_MODEL_VERSION", "").strip()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "").strip()
    if version.casefold() in forbidden or deployment.casefold() in forbidden:
        return _trip("model-pin", False, f"floating alias configured version={version!r} deployment={deployment!r}")
    if version and version not in allowed:
        return _trip("model-pin", False, f"unregistered model version {version!r}")
    if deployment and deployment not in allowed:
        return _trip("model-pin", False, f"unregistered deployment {deployment!r}")
    source = _read("services/integration/azure/openai.py")
    if "floating_alias" not in source:
        return _trip("model-pin", False, "adapter no longer refuses floating aliases")
    return _trip("model-pin", True, "configured model is pinned or unset; adapter refuses aliases")


def trip_residency() -> dict[str, object]:
    policy = _load_json("compliance/eu-ai-act/residency-policy.json")
    permitted = {str(item) for item in policy.get("permitted_regions") or []}
    if not permitted:
        return _trip("residency", False, "residency policy has no permitted regions")
    region = os.environ.get("AZURE_OPENAI_REGION", "").strip()
    if region and region not in permitted:
        return _trip("residency", False, f"configured region {region!r} is outside the analysed set")
    return _trip("residency", True, "configured region is unset or inside the analysed set")


def trip_deny_list() -> dict[str, object]:
    try:
        assert_baseline()
    except DenyListError as exc:
        return _trip("deny-list", False, str(exc))
    return _trip("deny-list", True, "deny-list still contains every baseline phrase")


def trip_thresholds() -> dict[str, object]:
    current = _parse_simple_yaml("evals/thresholds.yaml")
    baseline = _parse_simple_yaml("evals/thresholds.baseline.yaml")
    try:
        now = float(current.get("subgroup_spread_max") or "0")
        was = float(baseline.get("subgroup_spread_max") or "0")
    except ValueError:
        return _trip("thresholds", False, "subgroup_spread_max is not numeric")
    if now > was:
        return _trip("thresholds", False, f"subgroup_spread_max loosened {was} -> {now}")
    if (baseline.get("judge_gating") or "") == "true" and (current.get("judge_gating") or "") != "true":
        return _trip("thresholds", False, "judge_gating turned off")
    if (current.get("determinism_excluded_fields") or "") != (baseline.get("determinism_excluded_fields") or ""):
        return _trip("thresholds", False, "determinism_excluded_fields drifted without a baseline update")
    return _trip("thresholds", True, "hard eval gates are not looser than the frozen baseline")


def change_class_drift() -> list[str]:
    baseline = _load_json("compliance/iso42001/change-class-baseline.json")
    expected = baseline.get("files") or {}
    exceptions = _read("compliance/iso42001/exceptions.md")
    drifted: list[str] = []
    for rel in PROTECTED:
        digest = file_sha256(rel)
        recorded = str(expected.get(rel) or "")
        if digest == recorded:
            continue
        if rel in exceptions and "None recorded" not in exceptions:
            continue
        drifted.append(rel)
    return drifted


def trip_change_classes() -> dict[str, object]:
    drifted = change_class_drift()
    if drifted:
        return _trip("change-classes", False, "protected files changed without an exception: " + ", ".join(drifted))
    return _trip("change-classes", True, "protected change-class files match the signed baseline")


TRIPWIRES = (
    trip_write_tools,
    trip_human_review,
    trip_model_pin,
    trip_residency,
    trip_deny_list,
    trip_thresholds,
    trip_change_classes,
)


def evaluate() -> dict[str, object]:
    rows = control_map()
    unmapped: list[dict[str, str]] = []
    for row in rows:
        test_id = (row.get("test_id") or "").strip()
        evidence = (row.get("evidence_path") or "").strip()
        missing_cols = [name for name in REQUIRED_COLUMNS if name not in row]
        if missing_cols or not test_id or not evidence:
            unmapped.append(row)
            continue
        if not (_root() / evidence).is_file():
            unmapped.append(row)
            continue
        if not _test_path(test_id).is_file():
            unmapped.append(row)
    tripwires = [fn() for fn in TRIPWIRES]
    failed = [item for item in tripwires if not item["ok"]]
    return {
        "ok": not unmapped and not failed,
        "controls": len(rows),
        "unmapped": unmapped,
        "tripwires": tripwires,
        "claim": CLAIM,
        "failed": failed,
    }
