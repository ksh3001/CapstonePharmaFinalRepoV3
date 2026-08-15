"""Terminology versioning. A coding's version is part of its identity (INJ-039)."""

from __future__ import annotations

import csv
from pathlib import Path

from packages.config.paths import synthetic_dir
from packages.ontology.types import Coding


def _versions_path() -> Path:
    synthetic = synthetic_dir() / "data" / "terminology_versions.csv"
    if synthetic.is_file():
        return synthetic
    return Path(__file__).resolve().parents[2].parent / "fde-training-team3-pharma-project" / "data" / "terminology_versions.csv"


def load_terminology_versions(path: Path | None = None) -> tuple[dict[str, str], ...]:
    target = path if path is not None else _versions_path()
    rows: list[dict[str, str]] = []
    with target.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: (value or "").strip() for key, value in row.items()})
    return tuple(rows)


def retain_coding(term: str, dictionary: str, version: str) -> Coding:
    return Coding(term=term, dictionary=dictionary, version=version)


def equivalent(left: Coding, right: Coding) -> bool:
    """No threshold: same dictionary and same version, or not equivalent (plan §29.5)."""
    return (
        left.dictionary == right.dictionary
        and left.version == right.version
        and left.term == right.term
    )


def same_clinical_theme_not_equivalent(left: Coding, right: Coding) -> bool:
    """MedDRA 27.1 vs 28.0 remain distinct even when the clinical theme is similar."""
    return left.dictionary == right.dictionary and left.version != right.version
