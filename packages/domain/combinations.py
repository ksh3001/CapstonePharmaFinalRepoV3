"""Quasi-identifier combination refusal (BR-047, AC-FR005-19). Classification types live here (MR-5)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.config.privacy_thresholds import QUASI_IDENTIFIERS, REIDENTIFICATION_K
from packages.domain.batch import iter_records
from packages.domain.types import Abstention


def _source_name(source: str) -> str:
    return Path(source.replace("\\", "/")).name


def reidentification_assessment(fixture: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for source, record in iter_records(fixture):
        if _source_name(source) != "genomic_data.csv":
            continue
        rows.append(record)
    if not rows:
        return {"abstentions": [], "findings": [], "separate_fields": {}, "combination_withheld": False}

    counts: dict[tuple[str, ...], int] = {}
    for row in rows:
        key = tuple(str(row.get(field) or "") for field in QUASI_IDENTIFIERS)
        counts[key] = counts.get(key, 0) + 1
    below = any(count < REIDENTIFICATION_K for count in counts.values())
    separate: list[dict[str, Any]] = []
    for field in QUASI_IDENTIFIERS:
        values = sorted({str(row.get(field) or "") for row in rows if row.get(field) not in (None, "")})
        separate.append({"field": field, "values": values})
    findings: list[dict[str, Any]] = []
    abstentions: list[Abstention] = []
    if below:
        findings.append(
            {
                "finding_id": "F-REIDENT-COMBINATION",
                "statement": (
                    "A combination of individually permitted fields was withheld because it would "
                    "narrow a cohort below the re-identification threshold. Discriminating values are not named."
                ),
                "evidence_refs": ["data/genomic_data.csv"],
                "severity": "blocking",
            }
        )
        abstentions.append(
            Abstention(
                reason_code="reidentification_combination",
                subject_id="genomic_data.csv",
                statement="Combination withheld. Each field remains available separately.",
                threshold=REIDENTIFICATION_K,
            )
        )
    return {
        "abstentions": abstentions,
        "findings": findings,
        "separate_fields": separate,
        "combination_withheld": below,
        "joined_rows": [] if below else rows,
    }


def strip_joined_quasi(obj: Any) -> Any:
    """Drop a joined quasi-identifier tuple. Field inventories may remain separate."""
    if isinstance(obj, dict):
        present = [key for key in QUASI_IDENTIFIERS if key in obj]
        cleaned = dict(obj)
        if len(present) >= 2:
            for key in list(QUASI_IDENTIFIERS) + ["participant"]:
                cleaned.pop(key, None)
        return {key: strip_joined_quasi(value) for key, value in cleaned.items()}
    if isinstance(obj, list):
        return [strip_joined_quasi(item) for item in obj]
    return obj
