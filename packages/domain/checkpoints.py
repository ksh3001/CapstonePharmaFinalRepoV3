"""Resume classification types. Constructed only in domain (MR-5)."""

from __future__ import annotations

from typing import Any

from packages.domain.types import Abstention


def stale_checkpoint_abstention(subject_id: str, detail: str) -> Abstention:
    return Abstention(
        reason_code="checkpoint_stale",
        subject_id=subject_id,
        statement="Automatic resume is blocked; human confirmation is required before a fresh interrupt.",
        detail=detail,
    )


def hash_mismatch_finding(subject_id: str, stored: str, current: str) -> dict[str, Any]:
    return {
        "finding_id": f"F-CHECKPOINT-{subject_id}",
        "statement": (
            f"Checkpoint input hash does not match current source hash. "
            f"Resume is blocked. stored={stored} current={current}."
        ),
        "evidence_refs": [subject_id],
        "severity": "blocking",
    }
