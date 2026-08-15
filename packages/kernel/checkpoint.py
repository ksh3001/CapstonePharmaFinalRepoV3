"""Idempotent replay and checkpoint freshness (BR-030, BR-052, INJ-080)."""

from __future__ import annotations

import json
from typing import Any

from packages.config.checkpoint import MAX_STATE_AGE_MINUTES
from packages.domain.batch import iter_records
from packages.kernel.audit import write_audit
from packages.kernel.canonical import dumps, sha256_bytes
from packages.kernel.context import rule_context

_REPLAY: dict[str, bytes] = {}
_STEP_STATES: list[dict[str, Any]] = []


def reset_replay() -> None:
    _REPLAY.clear()
    _STEP_STATES.clear()


def input_hash(context: dict[str, Any], scenario_id: str) -> str:
    return sha256_bytes(dumps({"context": rule_context(context), "scenario_id": scenario_id}))


def drafts_from_run(record: dict[str, Any]) -> list[dict[str, Any]]:
    text = str(record.get("draft_reservations") or "")
    return [
        {
            "draft_id": part.strip(),
            "status": "draft",
            "no_side_effects": True,
            "statement": "Description only. The name of a record grants no power.",
        }
        for part in text.split(";")
        if part.strip()
    ]


def checkpoint_from_fixture(fixture: dict[str, Any], context: dict[str, Any]) -> dict[str, Any] | None:
    explicit = context.get("checkpoint")
    if isinstance(explicit, dict) and explicit:
        return dict(explicit)
    for _source, record in iter_records(fixture):
        if record.get("checkpoint") or record.get("run_id"):
            return {
                "run_id": str(record.get("run_id") or ""),
                "checkpoint_id": str(record.get("checkpoint") or ""),
                "state_age_minutes": record.get("state_age_minutes"),
                "draft_reservations": str(record.get("draft_reservations") or ""),
                "resume_result": str(record.get("resume_result") or ""),
                "input_hash": str(record.get("input_hash") or ""),
            }
    return None


def evaluate_checkpoint(
    checkpoint: dict[str, Any] | None,
    current_hash: str,
    *,
    max_age: int = MAX_STATE_AGE_MINUTES,
) -> dict[str, Any]:
    if not checkpoint:
        return {"fresh": True, "resume": False, "reason": ""}
    age_raw = checkpoint.get("state_age_minutes")
    try:
        age = int(str(age_raw)) if age_raw not in (None, "") else None
    except ValueError:
        age = None
    if age is not None and age > max_age:
        write_audit({"event": "checkpoint_stale", "state_age_minutes": age, "max_age": max_age})
        return {
            "fresh": False,
            "resume": False,
            "reason": "CHECKPOINT_STALE",
            "state_age_minutes": age,
            "max_age": max_age,
        }
    stored = str(checkpoint.get("input_hash") or checkpoint.get("hash") or "")
    if stored and stored != current_hash:
        write_audit({"event": "checkpoint_hash_mismatch", "stored": stored, "current": current_hash})
        return {
            "fresh": False,
            "resume": False,
            "reason": "CHECKPOINT_HASH_MISMATCH",
            "stored": stored,
            "current": current_hash,
        }
    return {"fresh": True, "resume": True, "reason": ""}


def take_replay(request_id: str) -> dict[str, Any] | None:
    payload = _REPLAY.get(request_id)
    if payload is None:
        return None
    write_audit({"event": "replay", "request_id": request_id})
    return json.loads(payload.decode("utf-8"))


def store_replay(request_id: str, pack: dict[str, Any]) -> None:
    _REPLAY[request_id] = dumps(pack)


def persist_step_checkpoint(state: dict[str, Any]) -> None:
    payload = dict(state)
    write_audit(
        {
            "event": "checkpoint_sync",
            "request_id": payload.get("request_id"),
            "step": payload.get("step"),
            "durability": "sync",
        }
    )
    _STEP_STATES.append(payload)


def step_checkpoints() -> list[dict[str, Any]]:
    return list(_STEP_STATES)


def record_agency_attempt(request_id: str, step: str) -> None:
    write_audit(
        {
            "event": "excessive_agency",
            "request_id": request_id,
            "step": step,
            "decision": "refused",
        }
    )
