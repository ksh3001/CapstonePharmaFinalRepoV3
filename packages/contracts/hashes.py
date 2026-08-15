"""Published source-artefact hashes from FILE_HASHES.csv (AMB-02)."""

from __future__ import annotations

import csv
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _hash_tables() -> list[Path]:
    candidates = [
        _REPO_ROOT / "tests" / "fixtures" / "synthetic" / "FILE_HASHES.csv",
        _REPO_ROOT / "FILE_HASHES.csv",
        _REPO_ROOT.parent / "fde-training-team3-pharma-project" / "FILE_HASHES.csv",
    ]
    return [path for path in candidates if path.is_file()]


def load_file_hashes() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for table in _hash_tables():
        with table.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                path = (row.get("path") or "").replace("\\", "/").strip()
                digest = (row.get("sha256") or "").strip().lower()
                if path and digest:
                    mapping[path] = digest
    return mapping


def published_hash(source_path: str) -> str | None:
    normalised = source_path.replace("\\", "/").lstrip("./")
    hashes = load_file_hashes()
    if normalised in hashes:
        return hashes[normalised]
    keyed = {Path(key).as_posix(): value for key, value in hashes.items()}
    return keyed.get(normalised)
