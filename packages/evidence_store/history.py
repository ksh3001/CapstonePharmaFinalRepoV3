"""Read reviewer actions from the append-only evidence chain."""

from __future__ import annotations

from typing import Any

from packages.evidence_store.chain import load_chain, store_root

DECISION_EVENTS = frozenset({"acknowledge", "contest", "acknowledge_refused"})
TRAIL_EVENTS = frozenset({"evidence_opened"})
REVIEW_EVENTS = DECISION_EVENTS | TRAIL_EVENTS
WORKFLOW_HREF = {
    "batch_evidence": "batch",
    "pv_intake": "pv",
    "supply_options": "supply",
    "batch": "batch",
    "pv": "pv",
    "supply": "supply",
}


def list_review_events() -> list[dict[str, Any]]:
    folder = store_root() / "chains"
    rows: list[dict[str, Any]] = []
    if not folder.is_dir():
        return rows
    for path in sorted(folder.glob("*.jsonl")):
        request_id = path.stem
        for row in load_chain(request_id):
            item = _as_review_event(request_id, row)
            if item is not None:
                rows.append(item)
    return rows


def _as_review_event(request_id: str, row: dict[str, Any]) -> dict[str, Any] | None:
    kind = str(row.get("type") or "")
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    event = str(payload.get("event") or "")
    payload_kind = str(payload.get("kind") or "")
    if kind == "review":
        if event not in REVIEW_EVENTS:
            event = event or "review"
    elif kind == "audit" and payload_kind in {"reviewer_action", "reviewer_follow_up"}:
        if event not in REVIEW_EVENTS:
            event = event or "review"
    else:
        return None
    workflow = str(payload.get("workflow") or "")
    entity = str(payload.get("entity") or "")
    href_key = WORKFLOW_HREF.get(workflow, "")
    href = f"/workflows/{href_key}/{entity}" if href_key and entity else ""
    return {
        "request_id": request_id,
        "seq": int(row.get("seq") or 0),
        "entry_hash": str(row.get("entry_hash") or ""),
        "event": event,
        "user": str(payload.get("user") or ""),
        "reason": str(payload.get("reason") or ""),
        "action_taken": str(payload.get("action_taken") or ""),
        "subject_id": str(payload.get("subject_id") or ""),
        "entity": entity,
        "product": str(payload.get("product") or ""),
        "workflow": workflow,
        "as_of": str(payload.get("as_of") or ""),
        "pack_hash": str(payload.get("pack_hash") or ""),
        "href": href,
        "signature": False,
        "execution": False,
        "decision": event in DECISION_EVENTS,
    }
