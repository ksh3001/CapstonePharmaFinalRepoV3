"""Orchestration classification types. Constructed only here (MR-5)."""

from __future__ import annotations

from typing import Any

from packages.domain.types import Abstention


def budget_stop_abstention(subject_id: str, exhausted: str) -> Abstention:
    return Abstention(
        reason_code="budget_stop",
        subject_id=subject_id,
        statement=(
            "The run stopped because a declared budget was exhausted. "
            "This pack is a complete budget-stop abstention."
        ),
        exhausted=exhausted,
    )


def undeclared_budget_abstention(subject_id: str) -> Abstention:
    return Abstention(
        reason_code="undeclared_budget",
        subject_id=subject_id,
        statement="The run refused to start because a required budget ceiling was not declared.",
    )


def retry_exhausted_abstention(subject_id: str, step: str) -> Abstention:
    return Abstention(
        reason_code="retry_exhausted",
        subject_id=subject_id,
        statement=(
            f"Step {step} failed repeatedly and terminated. "
            "A loop is a failure, not a strategy."
        ),
        step=step,
    )


def excessive_agency_finding(step: str) -> dict[str, Any]:
    return {
        "finding_id": f"F-AGENCY-{step}",
        "statement": f"Proposed step {step} is outside the declared graph and was refused.",
        "evidence_refs": [step],
        "severity": "blocking",
    }
