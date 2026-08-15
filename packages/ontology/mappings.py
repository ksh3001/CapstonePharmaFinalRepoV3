"""Load approved-mapping registers. Status other than approved never yields equivalence."""

from __future__ import annotations

import csv
from pathlib import Path

from packages.config.paths import synthetic_dir
from packages.ontology.types import BLOCKING_MAPPING_STATUS


def _open_csv(relative: str) -> Path:
    synthetic = synthetic_dir() / relative
    if synthetic.is_file():
        return synthetic
    fallback = Path(__file__).resolve().parents[2].parent / "fde-training-team3-pharma-project" / relative
    return fallback


def load_unit_mappings(path: Path | None = None) -> tuple[dict[str, str], ...]:
    target = path if path is not None else _open_csv("data/interface_mappings.csv")
    rows: list[dict[str, str]] = []
    with target.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: (value or "").strip() for key, value in row.items()})
    return tuple(rows)


def load_idmp_mappings(path: Path | None = None) -> tuple[dict[str, str], ...]:
    target = path if path is not None else _open_csv("data/idmp_mappings.csv")
    rows: list[dict[str, str]] = []
    with target.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: (value or "").strip() for key, value in row.items()})
    return tuple(rows)


def is_approved_status(status: str) -> bool:
    normalised = (status or "").strip().lower()
    if normalised in {"approved", "yes", "true"}:
        return True
    if normalised in BLOCKING_MAPPING_STATUS:
        return False
    return False
