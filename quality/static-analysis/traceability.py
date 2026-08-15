"""Traceability validator: AP → FR → BR → AC → TASK → test → evidence and inject → BR → AC."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from inject_coverage_gate import evaluate as evaluate_injects

_REPO_ROOT = Path(__file__).resolve().parents[2]
AP_RE = re.compile(r"\bAP-\d+\b")
FR_RE = re.compile(r"\bFR-\d{3}\b")
BR_RE = re.compile(r"\bBR-\d+[a-z]?\b")
AC_RE = re.compile(r"\bAC-FR\d+-\d+[a-z]?\b")
TASK_RE = re.compile(r"\bTASK-\d{3}\b")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _seed_rows() -> list[dict[str, str]]:
    from inject_coverage_gate import load_inject_ids, scan_acceptance_criteria, scan_business_rules

    known = set(load_inject_ids())
    br_text = _read(_REPO_ROOT / "specs" / "registers" / "business_rules_register.md")
    ac_text = _read(_REPO_ROOT / "specs" / "registers" / "acceptance_criteria_register.md")
    br_map = scan_business_rules(br_text, known)
    ac_map = scan_acceptance_criteria(ac_text, known)
    plan = _read(_REPO_ROOT / "specs" / "testing" / "ac_test_plan.md")
    feature_index = _read(_REPO_ROOT / "specs" / "features" / "FEATURE_INDEX.md")
    scope = _read(_REPO_ROOT / "specs" / "product" / "scope.md")
    aps = sorted(set(AP_RE.findall(scope)))
    rows: list[dict[str, str]] = []
    for br_id, injects in sorted(br_map.items()):
        br_line = next((line for line in br_text.splitlines() if line.startswith(f"| {br_id} ")), "")
        fr_ids = FR_RE.findall(br_line) or FR_RE.findall(feature_index)
        ac_ids = AC_RE.findall(br_line)
        for ac_id in ac_ids or [""]:
            test_line = next((line for line in plan.splitlines() if ac_id and ac_id in line), "")
            tasks = ",".join(sorted(set(TASK_RE.findall(test_line))))
            tests = ""
            if test_line:
                cells = [part.strip() for part in test_line.strip().strip("|").split("|")]
                tests = cells[3] if len(cells) > 3 else ""
            inject_ids = sorted(injects | ac_map.get(ac_id, set()))
            rows.append(
                {
                    "ap_id": ",".join(aps[:1]),
                    "fr_id": ",".join(fr_ids),
                    "br_id": br_id,
                    "ac_id": ac_id,
                    "task_id": tasks,
                    "test": tests,
                    "evidence": "specs/registers/business_rules_register.md",
                    "inject_id": ",".join(inject_ids),
                }
            )
    return rows


def write_traceability_csv(path: Path | None = None) -> Path:
    target = path if path is not None else _REPO_ROOT / "specs" / "registers" / "traceability.csv"
    rows = _seed_rows()
    fieldnames = ["ap_id", "fr_id", "br_id", "ac_id", "task_id", "test", "evidence", "inject_id"]
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return target


def evaluate() -> list[str]:
    errors: list[str] = []
    csv_path = _REPO_ROOT / "specs" / "registers" / "traceability.csv"
    if not csv_path.is_file():
        write_traceability_csv(csv_path)
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if "inject_id" not in (rows[0] if rows else {"inject_id": ""}):
        errors.append("traceability.csv is missing inject_id column")
    missing_ac = [row["br_id"] for row in rows if not (row.get("ac_id") or "").strip()]
    if missing_ac:
        errors.append("BR without AC: " + ", ".join(sorted(set(missing_ac))[:20]))
    inject_report = evaluate_injects()
    errors.extend(inject_report.errors)
    return errors


def assert_traceable() -> None:
    errors = evaluate()
    if errors:
        raise SystemExit("traceability validator failed:\n" + "\n".join(errors))
