"""Cross-domain complaint/batch/ICSR candidates (BR-019, AMB-05b)."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from packages.config.matching import LINKAGE_WINDOW_DAYS
from packages.domain.batch import iter_records
from packages.domain.types import Abstention

_DATE_KEYS = ("awareness_date", "event_date", "date", "timestamp", "onset")
_ID_KEYS = ("lot", "batch_id", "lots")


def _as_date(value: str) -> date | None:
    text = (value or "").strip()[:10]
    if len(text) != 10:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _record_date(record: dict[str, Any]) -> date | None:
    for key in _DATE_KEYS:
        parsed = _as_date(str(record.get(key) or ""))
        if parsed is not None:
            return parsed
    return None


def _identifiers(record: dict[str, Any]) -> set[str]:
    found: set[str] = set()
    for key in _ID_KEYS:
        raw = str(record.get(key) or "").strip()
        if not raw:
            continue
        for part in raw.replace(";", ",").split(","):
            token = part.strip()
            if token:
                found.add(token)
    return found


def _kind(source: str, record: dict[str, Any]) -> str:
    name = Path(source.replace("\\", "/")).name
    if "complaint" in name or record.get("complaint_id"):
        return "complaint"
    if "icsr" in name or record.get("case_id"):
        return "icsr"
    return "batch"


def cross_domain_candidates(fixture: dict[str, Any]) -> dict[str, Any]:
    """Shared lot/batch within ±30 days → unconfirmed_link. Outside the window → absent."""
    rows: list[dict[str, Any]] = []
    for source, record in iter_records(fixture):
        ids = _identifiers(record)
        when = _record_date(record)
        if not ids or when is None:
            continue
        rows.append(
            {
                "kind": _kind(source, record),
                "ids": ids,
                "when": when,
                "record_id": str(
                    record.get("complaint_id")
                    or record.get("case_id")
                    or record.get("batch_id")
                    or record.get("lot")
                    or ""
                ),
            }
        )
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for left in rows:
        for right in rows:
            if left is right or left["kind"] == right["kind"]:
                continue
            shared = left["ids"] & right["ids"]
            if not shared:
                continue
            distance = abs((left["when"] - right["when"]).days)
            if distance > LINKAGE_WINDOW_DAYS:
                continue
            identifier = sorted(shared)[0]
            pair = tuple(sorted((left["record_id"], right["record_id"])) + [identifier])
            if pair in seen:
                continue
            seen.add(pair)
            candidates.append(
                {
                    "kind": "unconfirmed_link",
                    "shared_identifier": identifier,
                    "time_distance_days": distance,
                    "left": {"kind": left["kind"], "record_id": left["record_id"]},
                    "right": {"kind": right["kind"], "record_id": right["record_id"]},
                    "window_days": LINKAGE_WINDOW_DAYS,
                    "statement": (
                        "Shared identifier within the linkage window is an unconfirmed_link candidate. "
                        "No causal or quality relationship is asserted."
                    ),
                }
            )
    candidates.sort(
        key=lambda item: (
            str(item.get("shared_identifier") or ""),
            str(item["left"]["record_id"]),
            str(item["right"]["record_id"]),
        )
    )
    return {"unconfirmed_links": candidates, "count": len(candidates)}


def unconfirmed_link_abstention(subject_id: str) -> Abstention:
    return Abstention(
        reason_code="unconfirmed_link",
        subject_id=subject_id,
        statement="Association below the shared-identifier and window bar is not confirmed.",
    )
