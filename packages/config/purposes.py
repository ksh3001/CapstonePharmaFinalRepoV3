"""Declared purposes. An unregistered purpose is never inferred (BR-041, INJ-063)."""

from __future__ import annotations

# capstone_evaluation is the challenge authorised_context purpose; it does not replace subject consent.
PURPOSE_REGISTER = frozenset(
    {
        "capstone_evaluation",
        "trial",
        "trial_and_biomarker",
        "biomarker",
        "biomarker_model",
        "pv_intake",
        "pharmacovigilance",
        "batch_evidence",
        "supply",
        "quality_review",
    }
)

CONSENT_PURPOSES = frozenset({"trial", "trial_and_biomarker", "biomarker", "biomarker_model"})
BIOMARKER_PURPOSES = frozenset({"biomarker", "biomarker_model"})
EVALUATION_PURPOSES = frozenset({"capstone_evaluation"})
