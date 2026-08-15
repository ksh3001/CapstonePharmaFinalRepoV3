"""Duplicate-candidate cut points. AMB-05a — POC defaults, not a validated PV rule."""

from __future__ import annotations

# Owned by the safety physician role (spec_ambiguities.md AMB-05a).
ONSET_WINDOW_DAYS = 7
DUPLICATE_SURFACE_MIN = 3
DUPLICATE_HIGH_SCORE = 6
COMPOSITE_FIELDS = (
    "patient_id",
    "dob_or_age",
    "sex",
    "product",
    "reaction",
    "onset",
)
BAND_HIGH = "duplicate_candidate_high"
BAND_MID = "duplicate_candidate"
BAND_WEAK = "duplicate_candidate_weak"
CONFIG_STATUS = "AMB-05a"
LINKAGE_WINDOW_DAYS = 30
LINKAGE_CONFIG_STATUS = "AMB-05b"
