"""ICSR duplicate candidates. Pairwise scores; never a merge (BR-014, plan §29.2)."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping

from packages.config.matching import (
    BAND_HIGH,
    BAND_MID,
    BAND_WEAK,
    COMPOSITE_FIELDS,
    CONFIG_STATUS,
    DUPLICATE_HIGH_SCORE,
    DUPLICATE_SURFACE_MIN,
    ONSET_WINDOW_DAYS,
)

_MISSING = frozenset({"", "unknown", "unk", "n/a", "na", "none"})
MERGE_KEYS = frozenset({"merged", "master_case", "master", "canonical_case", "cluster_id"})


def _present(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text or text.lower() in _MISSING:
        return None
    return text


def _parse_day(value: Any) -> date | None:
    text = _present(value)
    if text is None or "T" in text:
        text = text.split("T", 1)[0] if text else None
    if text is None:
        return None
    try:
        year, month, day = text.split("-")
        return date(int(year), int(month), int(day))
    except (TypeError, ValueError):
        return None


def _canonical_product(value: str | None, aliases: Mapping[str, str]) -> str | None:
    if value is None:
        return None
    return aliases.get(value) or aliases.get(value.upper()) or value


def _field_values(case: Mapping[str, Any], aliases: Mapping[str, str]) -> dict[str, Any]:
    patient = _present(case.get("patient_id") or case.get("patient_key") or case.get("initials"))
    dob = _present(case.get("date_of_birth") or case.get("dob"))
    age = _present(case.get("age_bucket") or case.get("age"))
    return {
        "worldwide_unique_id": _present(case.get("worldwide_unique_id") or case.get("wwuid")),
        "patient_id": patient,
        "dob_or_age": dob or age,
        "sex": (_present(case.get("sex")) or "").casefold() or None,
        "product": _canonical_product(_present(case.get("product") or case.get("suspect_product")), aliases),
        "reaction": _present(case.get("reaction_pt") or case.get("pt") or case.get("event") or case.get("reaction")),
        "onset": _parse_day(case.get("onset_date") or case.get("onset")),
        "case_id": str(case.get("case_id") or ""),
    }


def _onset_match(left: date | None, right: date | None, window_days: int) -> bool:
    if left is None or right is None:
        return False
    return abs((left - right).days) <= window_days


def _band(score: int, *, exact_id: bool) -> str | None:
    if exact_id or score >= DUPLICATE_HIGH_SCORE:
        return BAND_HIGH
    if score >= 4:
        return BAND_MID
    if score >= DUPLICATE_SURFACE_MIN:
        return BAND_WEAK
    return None


def compare_pair(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    *,
    product_aliases: Mapping[str, str] | None = None,
    window_days: int = ONSET_WINDOW_DAYS,
) -> dict[str, Any] | None:
    aliases = dict(product_aliases or {})
    a = _field_values(left, aliases)
    b = _field_values(right, aliases)
    case_a, case_b = sorted((a["case_id"], b["case_id"]))
    exact_id = bool(a["worldwide_unique_id"] and a["worldwide_unique_id"] == b["worldwide_unique_id"])
    matched: list[str] = []
    mismatched: list[str] = []
    for name in COMPOSITE_FIELDS:
        left_value = a[name]
        right_value = b[name]
        if name == "onset":
            hit = _onset_match(left_value, right_value, window_days)
        else:
            hit = left_value is not None and right_value is not None and left_value == right_value
        if hit:
            matched.append(name)
        else:
            mismatched.append(name)
    score = 6 if exact_id else len(matched)
    band = _band(score if not exact_id else DUPLICATE_HIGH_SCORE, exact_id=exact_id)
    if band is None:
        return None
    if exact_id:
        score = DUPLICATE_HIGH_SCORE
        strategy = "worldwide_unique_id"
    else:
        strategy = "composite"
    return {
        "case_a": case_a,
        "case_b": case_b,
        "score": score,
        "band": band,
        "matched_fields": matched,
        "mismatched_fields": mismatched,
        "strategy": strategy,
        "window_days": window_days,
        "config_status": CONFIG_STATUS,
    }


def find_duplicate_candidates(
    cases: list[Mapping[str, Any]],
    *,
    product_aliases: Mapping[str, str] | None = None,
    window_days: int = ONSET_WINDOW_DAYS,
) -> list[dict[str, Any]]:
    """Pairwise candidates. Not transitively closed. Score ≤2 is omitted, not recorded as a negative."""
    found: list[dict[str, Any]] = []
    for index, left in enumerate(cases):
        for right in cases[index + 1 :]:
            row = compare_pair(left, right, product_aliases=product_aliases, window_days=window_days)
            if row is not None:
                found.append(row)
    return sorted(found, key=lambda item: (item["case_a"], item["case_b"], item["band"]))
