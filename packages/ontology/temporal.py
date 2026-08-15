"""Temporal model. Source timestamps are verbatim; the clock is never sampled."""

from __future__ import annotations

import re
from datetime import date

from packages.ontology.types import BackEntryFlag, TimeBasis, TimePoint

TZ_MARK = re.compile(r"(Z|[+-]\d{2}:?\d{2})$")
DATE_ONLY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def timezone_known(value: str) -> bool:
    return TZ_MARK.search((value or "").strip()) is not None


def precision_of(value: str) -> str:
    text = (value or "").strip()
    if DATE_ONLY.match(text):
        return "date"
    if "T" in text and timezone_known(text):
        return "datetime_tz"
    if "T" in text:
        return "datetime"
    return "verbatim"


def preserve_time(value: str, *, basis: TimeBasis) -> TimePoint:
    text = value if value is not None else ""
    return TimePoint(
        value=text,
        precision=precision_of(text),
        timezone_known=timezone_known(text),
        basis=basis,
    )


def _parse_date(value: str) -> date | None:
    text = (value or "").strip()
    if text.endswith("Z"):
        text = text[:-1]
    if "T" in text:
        text = text.split("T", 1)[0]
    if DATE_ONLY.match(text):
        try:
            return date.fromisoformat(text)
        except ValueError:
            return None
    return None


def back_entry(event_time: str, recorded_at: str) -> BackEntryFlag:
    """AMB-11 default: flag any difference greater than zero and report magnitude."""
    if event_time == recorded_at:
        return BackEntryFlag(flagged=False, event_time=event_time, recorded_at=recorded_at, magnitude="0")
    left = _parse_date(event_time)
    right = _parse_date(recorded_at)
    if left is not None and right is not None:
        days = (right - left).days
        magnitude = f"{days}d"
    else:
        magnitude = "unparsed_difference"
    return BackEntryFlag(
        flagged=True,
        event_time=event_time,
        recorded_at=recorded_at,
        magnitude=magnitude,
    )
