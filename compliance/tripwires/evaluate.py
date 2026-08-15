"""Executable EU AI Act / ISO 42001 tripwires from the control map."""

from __future__ import annotations

import csv
from pathlib import Path

from packages.config.paths import repo_root


def control_map() -> list[dict[str, str]]:
    path = repo_root() / "compliance" / "control-map.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def evaluate() -> dict[str, object]:
    rows = control_map()
    missing = [row for row in rows if not (row.get("test_id") or "").strip() or not (row.get("evidence_path") or "").strip()]
    return {"ok": not missing, "controls": len(rows), "unmapped": missing}
