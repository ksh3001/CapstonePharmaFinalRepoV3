"""Write a complete per-request evidence chain. Fail closed when unwritable (BR-116)."""

from __future__ import annotations

from typing import Any

from packages.evidence_store.chain import OUTCOMES, StoreUnwritable, append_record, assert_writable, has_outcome
from packages.evidence_store.codec import dumps, sha256_bytes
from packages.evidence_store.scan import assert_clean_payload


def disposition_for(pack: dict[str, Any]) -> str:
    auth = str((pack.get("authorization") or {}).get("decision") or "")
    if auth == "deny":
        return "denied"
    reasons = {str(item.get("reason_code") or "") for item in pack.get("abstentions") or []}
    if "budget_stop" in reasons or "undeclared_budget" in reasons:
        return "budget_exhausted"
    if pack.get("gate_outcome") == "abstained" or "retry_exhausted" in reasons:
        return "abstained"
    return "completed"


def persist_run(
    pack: dict[str, Any],
    fixture: dict[str, Any] | None = None,
    *,
    audit_tail: list[dict[str, Any]] | None = None,
) -> None:
    request_id = str(pack.get("request_id") or "")
    if not request_id:
        raise StoreUnwritable("pack has no request_id")
    assert_writable()
    if has_outcome(request_id):
        return
    context = dict((fixture or {}).get("authorized_context") or {})
    append_record(
        request_id,
        "request",
        {
            "request_id": request_id,
            "scenario_id": pack.get("scenario_id") or (fixture or {}).get("scenario", {}).get("id"),
            "user": context.get("user") or (pack.get("authorization") or {}).get("user"),
            "purpose": context.get("purpose") or (pack.get("authorization") or {}).get("purpose"),
            "as_of": pack.get("as_of"),
            "mode": context.get("mode") or "assessment",
            "authorization": pack.get("authorization"),
        },
    )
    sources = []
    for blob in (fixture or {}).get("evidence") or []:
        sources.append({"source": blob.get("source"), "sha256": blob.get("sha256")})
    append_record(request_id, "inputs", {"sources": sources, "copyset": True})
    packed = dumps(pack)
    append_record(request_id, "pack", {"sha256": sha256_bytes(packed), "bytes": len(packed)})
    decisions = []
    for item in pack.get("abstentions") or []:
        decisions.append({"kind": "abstention", "reason_code": item.get("reason_code")})
    for item in pack.get("gaps") or []:
        decisions.append({"kind": "gap", "gap_type": item.get("gap_type")})
    for item in pack.get("contradictions") or []:
        decisions.append({"kind": "contradiction", "topic": item.get("topic")})
    if (pack.get("authorization") or {}).get("decision") == "deny":
        decisions.append({"kind": "denial", "reason": (pack.get("authorization") or {}).get("reason")})
    append_record(request_id, "decisions", {"items": decisions})
    append_record(request_id, "audit", {"events": list(audit_tail or [])})
    outcome = disposition_for(pack)
    if outcome not in OUTCOMES:
        outcome = "internal_error"
    if outcome in {"abstained", "denied"} and not decisions:
        append_record(request_id, "decisions", {"items": [{"kind": outcome}]})
    append_record(request_id, "outcome", {"disposition": outcome})


def persist_llm(request_id: str, result: dict[str, Any]) -> None:
    if not result.get("called"):
        return
    prompt = result.get("prompt")
    payload = {
        "deployment": result.get("deployment"),
        "model_version": result.get("model_version"),
        "api_version": result.get("api_version"),
        "system_fingerprint": result.get("system_fingerprint"),
        "content_filter": result.get("content_filter"),
        "prompt_sha256": sha256_bytes(dumps(prompt)) if prompt is not None else "",
        "outbound": result.get("outbound"),
        "prompt_tokens": int(result.get("prompt_tokens") or 0),
        "completion_tokens": int(result.get("completion_tokens") or 0),
        "total_tokens": int(result.get("total_tokens") or 0),
    }
    from packages.finops.rates import price_tokens

    priced = price_tokens(int(payload["prompt_tokens"]), int(payload["completion_tokens"]))
    if priced.get("priced"):
        payload["inference_cost"] = priced["inference_cost"]
        payload["prompt_cost"] = priced["prompt_cost"]
        payload["completion_cost"] = priced["completion_cost"]
        payload["input_per_million"] = priced["input_per_million"]
        payload["output_per_million"] = priced["output_per_million"]
        payload["cost_model"] = priced["model"]
        payload["cost_currency"] = priced["currency"]
    assert_clean_payload(payload)
    append_record(request_id, "llm", payload)
    guard = result.get("guard") or {}
    if guard:
        append_record(
            request_id,
            "guard",
            {"check": guard.get("check"), "passed": bool(guard.get("passed"))},
        )


def persist_review(request_id: str, action: dict[str, Any]) -> dict[str, Any]:
    """Append a reviewer action. Not a signature and not a regulated disposition."""
    if not request_id:
        raise StoreUnwritable("review has no request_id")
    payload = {
        "kind": "reviewer_action",
        "event": str(action.get("event") or ""),
        "user": str(action.get("user") or ""),
        "reason": str(action.get("reason") or ""),
        "action_taken": str(action.get("action_taken") or ""),
        "subject_id": str(action.get("subject_id") or ""),
        "entity": str(action.get("entity") or ""),
        "product": str(action.get("product") or ""),
        "workflow": str(action.get("workflow") or ""),
        "as_of": str(action.get("as_of") or ""),
        "pack_hash": str(action.get("pack_hash") or ""),
        "execution": False,
        "signature": False,
    }
    assert_clean_payload(payload)
    return append_record(request_id, "review", payload)
