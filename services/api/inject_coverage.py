"""Inject coverage for the console. Presentation of the inject-coverage gate, not a work queue."""

from __future__ import annotations

import csv
import importlib.util
import re
import sys
from typing import Any

from packages.config.paths import repo_root, synthetic_dir

_GATE_MODULE = None
_AC_ROW_RE = re.compile(r"^\|\s*(AC-FR\d+-\d+[a-z]?)\s*\|")
_TEST_PATH_RE = re.compile(r"`((?:tests|quality|docs)/[^`\s]+)`")
LANE_BY_DIMENSION = {
    "D04": "Batch",
    "D06": "PV intake",
    "D08": "Supply",
}


def _gate_module() -> Any:
    global _GATE_MODULE
    if _GATE_MODULE is not None:
        return _GATE_MODULE
    path = repo_root() / "quality" / "static-analysis" / "inject_coverage_gate.py"
    spec = importlib.util.spec_from_file_location("inject_coverage_gate", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load inject coverage gate from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("inject_coverage_gate", module)
    spec.loader.exec_module(module)
    _GATE_MODULE = module
    return module


def _load_participant_results() -> dict[str, str]:
    path = synthetic_dir() / "data" / "INJECT_TEST_COVERAGE.csv"
    if not path.is_file():
        return {}
    results: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            inject_id = str(row.get("inject_id") or "").strip()
            if inject_id:
                results[inject_id] = str(row.get("participant_result") or "").strip()
    return results


def _load_evidence_sources() -> dict[str, list[str]]:
    path = synthetic_dir() / "data" / "inject_evidence_map.csv"
    if not path.is_file():
        return {}
    sources: dict[str, list[str]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            inject_id = str(row.get("inject_id") or "").strip()
            raw = str(row.get("evidence_sources") or "").strip()
            if inject_id and raw:
                sources[inject_id] = [part.strip() for part in raw.split(";") if part.strip()]
    return sources


def _tests_by_ac() -> dict[str, list[str]]:
    path = repo_root() / "specs" / "testing" / "ac_test_plan.md"
    if not path.is_file():
        return {}
    mapping: dict[str, list[str]] = {}
    root = repo_root()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _AC_ROW_RE.match(line)
        if not match:
            continue
        ac_id = match.group(1)
        found: list[str] = []
        for rel in _TEST_PATH_RE.findall(line):
            if (root / rel).is_file() and rel not in found:
                found.append(rel)
        if found:
            mapping[ac_id] = found
    return mapping


def _lane(dimension: str) -> str:
    return LANE_BY_DIMENSION.get(dimension, "Shared")


def list_inject_coverage() -> list[dict[str, Any]]:
    """Return injects with rule coverage, challenge evidence, and verifying tests."""
    gate = _gate_module()
    report = gate.evaluate()
    injects = gate.load_inject_ids()
    allowlist = set(gate.CLOSED_ALLOWLIST)
    artefacts = (gate.load_allowlist() or {}).get("artefacts") or {}
    results = _load_participant_results()
    evidence = _load_evidence_sources()
    tests_for_ac = _tests_by_ac()
    root = repo_root()
    rows: list[dict[str, Any]] = []
    for digits in sorted(injects):
        item = injects[digits]
        inject_id = str(item.get("id") or f"INJ-{digits}")
        brs = sorted(report.br_by_inject.get(digits, ()))
        acs = sorted(report.ac_by_inject.get(digits, ()))
        meta = artefacts.get(digits) or {}
        artefact_path = str(meta.get("path") or "")
        verifying_test = str(meta.get("test") or "")
        artefact_ok = (
            digits in allowlist
            and artefact_path
            and verifying_test
            and (root / artefact_path).is_file()
            and (root / verifying_test).is_file()
        )
        tests: list[str] = []
        if artefact_ok and verifying_test not in tests:
            tests.append(verifying_test)
        for ac_id in acs:
            for rel in tests_for_ac.get(ac_id, ()):
                if rel not in tests:
                    tests.append(rel)
        if artefact_ok:
            coverage = "artefact"
            status_label = "Covered · artefact"
            covered = True
        elif brs and acs:
            coverage = "covered"
            status_label = "Covered"
            covered = True
        else:
            coverage = "uncovered"
            status_label = "Not covered"
            covered = False
        dimension = str(item.get("dimension") or "")
        rows.append(
            {
                "id": inject_id,
                "title": str(item.get("title") or ""),
                "dimension": dimension,
                "lane": _lane(dimension),
                "covered": covered,
                "coverage": coverage,
                "status_label": status_label,
                "business_rules": brs,
                "acceptance_criteria": acs,
                "artefact_path": artefact_path,
                "verifying_test": tests[0] if tests else verifying_test,
                "verifying_tests": tests,
                "evidence_sources": evidence.get(inject_id, []),
                "participant_result": results.get(inject_id, ""),
            }
        )
    return rows
