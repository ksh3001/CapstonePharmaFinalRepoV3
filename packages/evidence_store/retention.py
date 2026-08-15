"""Retention and live hold check. Hold state is never cached (BR-121)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from packages.evidence_store.chain import append_record

PROMPT_TTL_DAYS = 90
NEVER_EXPIRE = frozenset({"clinical_trial_source", "ICSR", "icsr", "clinical"})


def _as_of(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def live_holds(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for blob in fixture.get("evidence") or []:
        source = str(blob.get("source") or "").replace("\\", "/")
        if not source.endswith("legal_holds.csv"):
            continue
        for record in blob.get("records") or []:
            if isinstance(record, dict) and str(record.get("status") or "").casefold() == "active":
                found.append(record)
    return found


def maybe_expire_llm(
    request_id: str,
    *,
    recorded_at: str,
    as_of: str,
    record_type: str,
    fixture: dict[str, Any],
) -> dict[str, Any]:
    if record_type in NEVER_EXPIRE:
        return {"expired": False, "reason": "clinical_or_icsr_retained"}
    holds = live_holds(fixture)
    age = _as_of(as_of) - _as_of(recorded_at)
    if age < timedelta(days=PROMPT_TTL_DAYS):
        return {"expired": False, "reason": "within_ttl"}
    if holds:
        append_record(
            request_id,
            "hold_refusal",
            {
                "holds": [str(row.get("hold_id") or "") for row in holds],
                "record_type": record_type,
            },
        )
        return {
            "expired": False,
            "reason": "legal_hold",
            "holds": [str(row.get("hold_id") or "") for row in holds],
        }
    if record_type in {"llm", "AI prompt logs", "prompt"}:
        append_record(request_id, "expiry", {"record_type": record_type, "ttl_days": PROMPT_TTL_DAYS})
        return {"expired": True, "reason": "ttl"}
    return {"expired": False, "reason": "not_prompt_log"}
