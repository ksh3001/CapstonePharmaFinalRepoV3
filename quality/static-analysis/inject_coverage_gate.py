"""Inject-coverage gate: every behavioural inject has a BR and an AC. Closed allow-list of 001–003."""

from __future__ import annotations

import json
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
CLOSED_ALLOWLIST = frozenset({"001", "002", "003"})
EXPECTED_INJECT_COUNT = 84
INJECT_RE = re.compile(r"INJ-(\d{3})", re.IGNORECASE)
BR_ROW_RE = re.compile(r"^\|\s*(BR-\d+[a-z]?)\s*\|")
AC_ROW_RE = re.compile(r"^\|\s*(AC-FR\d+-\d+[a-z]?)\s*\|")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_inject_ids(injects_path: Path | None = None) -> dict[str, dict]:
    path = injects_path if injects_path is not None else _REPO_ROOT / "data" / "injects.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, dict] = {}
    for item in payload:
        raw = str(item["id"])
        digits = raw.replace("INJ-", "").replace("inj-", "").zfill(3)
        result[digits] = item
    return result


def load_allowlist(path: Path | None = None) -> dict:
    target = path if path is not None else _HERE / "inject_coverage_allowlist.json"
    return _load_json(target)


def extract_inject_ids(text: str, known: set[str] | None = None) -> set[str]:
    found: set[str] = set()
    for match in INJECT_RE.finditer(text):
        found.add(match.group(1))
    stripped = INJECT_RE.sub(" ", text)
    stripped = re.sub(r"PUB-\d+", " ", stripped)
    stripped = re.sub(r"AC-FR\d+-\d+[a-z]?", " ", stripped)
    stripped = re.sub(r"BR-\d+[a-z]?", " ", stripped)
    stripped = re.sub(r"FR-\d+", " ", stripped)
    stripped = re.sub(r"TASK-\d+", " ", stripped)
    for match in re.finditer(r"\b(\d{3})\b", stripped):
        found.add(match.group(1))
    return found


def _table_cells(line: str) -> list[str]:
    parts = [part.strip() for part in line.strip().strip("|").split("|")]
    return parts


def scan_business_rules(text: str, known: set[str]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for line in text.splitlines():
        match = BR_ROW_RE.match(line)
        if not match:
            continue
        cells = _table_cells(line)
        br_id = match.group(1)
        inject_cell = cells[-1] if cells else ""
        mapping.setdefault(br_id, set()).update(extract_inject_ids(inject_cell, known))
    return mapping


def scan_acceptance_criteria(text: str, known: set[str]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for line in text.splitlines():
        match = AC_ROW_RE.match(line)
        if not match:
            continue
        cells = _table_cells(line)
        ac_id = match.group(1)
        inject_cell = cells[-1] if cells else ""
        mapping.setdefault(ac_id, set()).update(extract_inject_ids(inject_cell, known))
    return mapping


class InjectCoverageReport:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.br_by_inject: dict[str, set[str]] = {}
        self.ac_by_inject: dict[str, set[str]] = {}
        self.unknown_in_registers: set[str] = set()
        self.allowlist_ids: set[str] = set()

    @property
    def ok(self) -> bool:
        return not self.errors


def evaluate(
    *,
    injects_path: Path | None = None,
    br_path: Path | None = None,
    ac_path: Path | None = None,
    allowlist_path: Path | None = None,
) -> InjectCoverageReport:
    report = InjectCoverageReport()
    injects = load_inject_ids(injects_path)
    known = set(injects)
    allowlist = load_allowlist(allowlist_path)
    allowed = {str(item).zfill(3) for item in allowlist.get("allowed_ids", [])}
    report.allowlist_ids = allowed
    extra = sorted(allowed - CLOSED_ALLOWLIST)
    if extra:
        report.errors.append(
            "inject allow-list contains IDs outside the closed artefact set "
            f"{sorted(CLOSED_ALLOWLIST)}: {extra}"
        )
    missing_closed = sorted(CLOSED_ALLOWLIST - allowed)
    if missing_closed:
        report.errors.append(f"inject allow-list dropped artefact IDs {missing_closed}")

    expected_ids = {f"{index:03d}" for index in range(1, EXPECTED_INJECT_COUNT + 1)}
    if set(injects) != expected_ids:
        missing_ids = ",".join(sorted(expected_ids - set(injects)))
        extra_ids = ",".join(sorted(set(injects) - expected_ids))
        report.errors.append(
            f"data/injects.json must contain INJ-001…{EXPECTED_INJECT_COUNT:03d} "
            f"({EXPECTED_INJECT_COUNT} injects); missing {missing_ids or 'none'}; extra {extra_ids or 'none'}"
        )

    artefacts = allowlist.get("artefacts") or {}
    for inject_id in sorted(CLOSED_ALLOWLIST):
        meta = artefacts.get(inject_id) or {}
        rel_path = str(meta.get("path") or "").strip()
        rel_test = str(meta.get("test") or "").strip()
        if not rel_path or not rel_test:
            report.errors.append(
                f"artefact inject {inject_id} is missing path or test in the allow-list"
            )
            continue
        if not (_REPO_ROOT / rel_path).is_file():
            report.errors.append(f"artefact inject {inject_id} is missing file {rel_path}")
        if not (_REPO_ROOT / rel_test).is_file():
            report.errors.append(f"artefact inject {inject_id} is missing test {rel_test}")

    br_file = br_path if br_path is not None else _REPO_ROOT / "specs" / "registers" / "business_rules_register.md"
    ac_file = ac_path if ac_path is not None else _REPO_ROOT / "specs" / "registers" / "acceptance_criteria_register.md"
    br_map = scan_business_rules(br_file.read_text(encoding="utf-8"), known)
    ac_map = scan_acceptance_criteria(ac_file.read_text(encoding="utf-8"), known)

    cited: set[str] = set()
    for br_id, ids in br_map.items():
        for inject_id in ids:
            cited.add(inject_id)
            report.br_by_inject.setdefault(inject_id, set()).add(br_id)
            if inject_id not in known:
                report.unknown_in_registers.add(inject_id)
    for ac_id, ids in ac_map.items():
        for inject_id in ids:
            cited.add(inject_id)
            report.ac_by_inject.setdefault(inject_id, set()).add(ac_id)
            if inject_id not in known:
                report.unknown_in_registers.add(inject_id)

    if report.unknown_in_registers:
        report.errors.append(
            "registers cite inject IDs absent from data/injects.json: "
            + ", ".join(sorted(report.unknown_in_registers))
        )

    behavioural = sorted(known - CLOSED_ALLOWLIST)
    uncovered: list[str] = []
    for inject_id in behavioural:
        has_br = bool(report.br_by_inject.get(inject_id))
        has_ac = bool(report.ac_by_inject.get(inject_id))
        if not has_br or not has_ac:
            uncovered.append(inject_id)
            missing = []
            if not has_br:
                missing.append("business rule")
            if not has_ac:
                missing.append("acceptance criterion")
            report.errors.append(
                f"inject {inject_id} is not carried by at least one {' and one '.join(missing)}"
            )
    return report


def assert_coverage(**kwargs: Path | None) -> InjectCoverageReport:
    report = evaluate(**kwargs)
    if not report.ok:
        raise SystemExit("inject-coverage gate failed:\n" + "\n".join(report.errors))
    return report
