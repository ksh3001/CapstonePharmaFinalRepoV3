"""Validated language scope for PV extraction (INJ-072)."""

from __future__ import annotations

# English and German are in validated extraction scope; Arabic and Hindi are not (INJ-072).
VALIDATED_LANGUAGES = frozenset({"english", "german"})
CRITERION_STATES = frozenset({"present", "absent", "unverifiable"})
MINIMUM_CRITERIA = (
    "identifiable_reporter",
    "identifiable_patient",
    "suspect_product",
    "event",
)
