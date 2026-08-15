"""Stdlib JSON API. FastAPI is optional transport; assessment calls these handlers."""

from __future__ import annotations

import json
from typing import Any

from packages.config.catalog import fixture_for, product_for
from packages.config.paths import synthetic_dir
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import SchemaError, validate
from packages.kernel.audit import write_audit
from packages.kernel.canonical import dumps
from scripts.build_fixture_copyset import build
from services.integration.langgraph.resolve import resolve_runtime_orchestrator

MUTATION_PATHS = (
    "/api/reviews/{request_id}/acknowledge",
    "/api/reviews/{request_id}/contest",
)
PROHIBITED_ACTION_TOKENS = (
    "release",
    "reject",
    "allocate",
    "reserve",
    "ship",
    "recall",
    "eligible",
    "disposition",
    "confirm-signal",
)

_OPENED: dict[str, set[str]] = {}
_PREPARERS: dict[str, str] = {}
_PACKS: dict[str, dict[str, Any]] = {}
_RESPONSES: dict[str, list[dict[str, Any]]] = {}


def reset_api_state() -> None:
    from services.api.engine_chat import reset_chat

    _OPENED.clear()
    _PREPARERS.clear()
    _PACKS.clear()
    _RESPONSES.clear()
    reset_chat()


def get_pack(request_id: str) -> dict[str, Any] | None:
    return _PACKS.get(request_id)


def _load_fixture(name: str) -> dict[str, Any]:
    folder = synthetic_dir() / "evaluation" / "public_fixtures"
    if not folder.is_dir():
        build()
    return json.loads((folder / name).read_text(encoding="utf-8"))


def _json_response(status: int, payload: dict[str, Any], *, headers: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "headers": {"content-type": "application/json", **(headers or {})},
        "body": dumps(payload).decode("utf-8"),
        "payload": payload,
    }


def _error(code: str, message: str, request_id: str, as_of: str, *, status: int = 400) -> dict[str, Any]:
    return _json_response(
        status,
        {
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
                "as_of": as_of,
                "retryable": False,
            }
        },
    )


def _validate_pack(pack: dict[str, Any], contract: str) -> dict[str, Any] | None:
    try:
        validate(pack, resolve_contract(contract))
    except SchemaError as exc:
        return _error("CONTRACT_INVALID", "Pack failed contract validation", pack.get("request_id") or "UNSET", str(pack.get("as_of") or ""), status=500)
    return None


def _remember(pack: dict[str, Any], *, user: str) -> dict[str, Any]:
    request_id = str(pack.get("request_id") or "")
    _PACKS[request_id] = pack
    _PREPARERS.setdefault(request_id, user)
    _OPENED.setdefault(request_id, set())
    return pack


def critical_record_ids(pack: dict[str, Any]) -> list[str]:
    cited: set[str] = set()
    for item in pack.get("gaps") or []:
        if item.get("subject_id"):
            cited.add(str(item["subject_id"]))
        for ref in item.get("evidence_refs") or []:
            cited.add(str(ref))
    for item in pack.get("contradictions") or []:
        if item.get("record_id"):
            cited.add(str(item["record_id"]))
    evidence_ids = {str(item.get("record_id") or "") for item in pack.get("evidence") or []}
    return sorted(item for item in cited if item in evidence_ids) or sorted(evidence_ids)


def outstanding_critical(request_id: str) -> list[str]:
    pack = _PACKS.get(request_id) or {}
    opened = _OPENED.get(request_id) or set()
    return [item for item in critical_record_ids(pack) if item not in opened]


def opened_record_ids(request_id: str) -> set[str]:
    return set(_OPENED.get(request_id) or ())


def handle(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    user: str = "participant_test_user",
    fixture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    method = method.upper()
    body = body or {}
    if method == "GET" and path.startswith("/api/workflows/batch/"):
        batch_id = path.rsplit("/", 1)[-1]
        fixture = _load_fixture(fixture_for("batch", batch_id))
        pack = resolve_runtime_orchestrator().run({"fixture": fixture, "workflow": "batch", "entity_id": batch_id})
        err = _validate_pack(pack, "batch_response.schema.json")
        if err:
            return err
        _remember(pack, user=user)
        return _json_response(200, pack)
    if method == "GET" and path.startswith("/api/workflows/pv/"):
        case_id = path.rsplit("/", 1)[-1]
        payload = fixture if fixture is not None else _load_fixture(fixture_for("pv", case_id))
        pack = resolve_runtime_orchestrator().run({"fixture": payload, "workflow": "pv", "entity_id": case_id})
        err = _validate_pack(pack, "pv_response.schema.json")
        if err:
            return err
        _remember(pack, user=user)
        return _json_response(200, pack)
    if method == "GET" and path.startswith("/api/workflows/supply/"):
        event_id = path.rsplit("/", 1)[-1]
        fixture = _load_fixture(fixture_for("supply", event_id))
        pack = resolve_runtime_orchestrator().run({"fixture": fixture, "workflow": "supply", "entity_id": event_id})
        err = _validate_pack(pack, "supply_response.schema.json")
        if err:
            return err
        _remember(pack, user=user)
        return _json_response(200, pack)
    if method == "GET" and path.startswith("/api/scenarios/"):
        scenario_id = path.rsplit("/", 1)[-1]
        payload = fixture if fixture is not None else _load_fixture(f"{scenario_id}.json")
        pack = resolve_runtime_orchestrator().run({"fixture": payload, "workflow": str((payload.get("scenario") or {}).get("workflow") or "security")})
        err = _validate_pack(pack, str(payload.get("response_contract") or "advisory_nonexecuting"))
        if err:
            return err
        _remember(pack, user=user)
        return _json_response(200, pack)
    if method == "GET" and path.startswith("/api/evidence/"):
        record_id = path.rsplit("/", 1)[-1]
        request_id = str(body.get("request_id") or "")
        pack = _PACKS.get(request_id) or {}
        item = next((row for row in pack.get("evidence") or [] if str(row.get("record_id") or "") == record_id), None)
        if item is None:
            return _error("SOURCE_UNAVAILABLE", "Evidence item is not in the current pack", request_id or "UNSET", str(pack.get("as_of") or ""))
        _OPENED.setdefault(request_id, set()).add(record_id)
        write_audit({"event": "evidence_opened", "request_id": request_id, "record_id": record_id, "user": user})
        _persist_review(
            request_id,
            event="evidence_opened",
            user=user,
            subject_id=record_id,
            session=False,
        )
        return _json_response(200, dict(item))
    if method == "GET" and path == "/api/health":
        from packages.kernel.audit import audit_events
        from packages.observability.health import runtime_health

        sessions = [
            {
                "request_id": request_id,
                "entity": pack_entity(pack),
                "product": pack_product(pack),
                "workflow": str(pack.get("workflow") or ""),
            }
            for request_id, pack in _PACKS.items()
        ]
        return _json_response(
            200,
            runtime_health(
                session_count=len(_PACKS),
                audit_events=audit_events(),
                sessions=sessions,
            ),
        )
    if method == "GET" and path == "/api/gates":
        return _json_response(200, {"gates": ["authz", "purpose", "residency", "hold", "tool", "model", "continuity"]})
    if method == "GET" and path == "/api/agents":
        from packages.config.agents import AGENT_IDS, load_agents

        roster = load_agents()
        return _json_response(
            200,
            {
                "agents": [
                    {"id": agent_id, **dict(roster[agent_id])}
                    for agent_id in AGENT_IDS
                    if agent_id in roster
                ]
            },
        )
    if method == "GET" and path == "/api/injects/coverage":
        from services.api.inject_coverage import list_inject_coverage

        rows = list_inject_coverage()
        counts = {
            "covered": sum(1 for item in rows if item.get("coverage") == "covered"),
            "artefact": sum(1 for item in rows if item.get("coverage") == "artefact"),
            "uncovered": sum(1 for item in rows if item.get("coverage") == "uncovered"),
        }
        return _json_response(200, {"injects": rows, "counts": counts})
    if method == "POST" and path == "/api/ask":
        from services.api.engine_chat import record_turn
        from services.integration.mcp.ask import answer_question

        question = str(body.get("q") or body.get("question") or "")
        payload = answer_question(question, user=user)
        record_turn(question, payload)
        return _json_response(200, payload)
    if method == "GET" and path == "/api/history":
        from packages.evidence_store.history import list_review_events

        rows = list_review_events()
        return _json_response(
            200,
            {
                "store": "evidence_chain",
                "advisory": True,
                "events": rows,
                "decisions": sum(1 for item in rows if item.get("decision")),
                "opened": sum(1 for item in rows if item.get("event") == "evidence_opened"),
            },
        )
    if method == "POST" and "/acknowledge" in path:
        request_id = path.split("/reviews/")[1].split("/")[0]
        return _acknowledge(
            request_id,
            user=user,
            as_of=str(body.get("as_of") or ""),
            action_taken=str(body.get("action_taken") or ""),
        )
    if method == "POST" and "/contest" in path:
        request_id = path.split("/reviews/")[1].split("/")[0]
        reason = str(body.get("reason") or "")
        action_taken = str(body.get("action_taken") or "")
        write_audit(
            {
                "event": "contest",
                "request_id": request_id,
                "user": user,
                "reason": reason,
                "action_taken": action_taken,
                "subject_id": str(body.get("subject_id") or ""),
                "signature": False,
            }
        )
        stored = _store_response(
            request_id,
            event="contest",
            user=user,
            reason=reason,
            action_taken=action_taken,
            subject_id=str(body.get("subject_id") or ""),
        )
        return _json_response(
            200,
            {
                "recorded": True,
                "signature": False,
                "request_id": request_id,
                "evidence_seq": stored.get("seq"),
                "label": "Follow-up recorded as evidence. Not a signature and not a regulated decision.",
            },
        )
    return _error("AUTHZ_DENIED", "Unknown route", "UNSET", "", status=404)


def _review_context(request_id: str) -> dict[str, str]:
    pack = _PACKS.get(request_id) or {}
    if not pack:
        return {"entity": "", "product": "", "workflow": "", "as_of": ""}
    return {
        "entity": pack_entity(pack),
        "product": pack_product(pack),
        "workflow": str(pack.get("workflow") or ""),
        "as_of": str(pack.get("as_of") or ""),
    }


def _persist_review(
    request_id: str,
    *,
    event: str,
    user: str,
    reason: str = "",
    action_taken: str = "",
    subject_id: str = "",
    pack_hash: str = "",
    session: bool = True,
) -> dict[str, Any]:
    entry = {
        "event": event,
        "user": user,
        "reason": reason,
        "action_taken": action_taken,
        "subject_id": subject_id,
        "signature": False,
        "execution": False,
    }
    if session:
        _RESPONSES.setdefault(request_id, []).append(entry)
        stored: dict[str, Any] = {"seq": len(_RESPONSES[request_id])}
    else:
        stored = {"seq": 0}
    try:
        from packages.evidence_store.chain import StoreUnwritable
        from packages.evidence_store.scan import StoreScanError
        from packages.evidence_store.writer import persist_review

        stored = persist_review(
            request_id,
            {
                **entry,
                **_review_context(request_id),
                "pack_hash": pack_hash,
            },
        )
    except (StoreUnwritable, StoreScanError, OSError, ValueError):
        stored = {"seq": stored.get("seq") or 0, "store": "memory"}
    return stored


def _store_response(
    request_id: str,
    *,
    event: str,
    user: str,
    reason: str = "",
    action_taken: str = "",
    subject_id: str = "",
    pack_hash: str = "",
) -> dict[str, Any]:
    return _persist_review(
        request_id,
        event=event,
        user=user,
        reason=reason,
        action_taken=action_taken,
        subject_id=subject_id,
        pack_hash=pack_hash,
        session=True,
    )


def list_follow_ups(request_id: str) -> list[dict[str, Any]]:
    return list(_RESPONSES.get(request_id) or [])


def pack_entity(pack: dict[str, Any]) -> str:
    case_ids = pack.get("case_ids") or []
    return str(
        pack.get("batch_id")
        or (case_ids[0] if case_ids else "")
        or pack.get("event_id")
        or pack.get("request_id")
        or ""
    )


def pack_product(pack: dict[str, Any]) -> str:
    href_key = {"batch_evidence": "batch", "pv_intake": "pv", "supply_options": "supply"}.get(
        str(pack.get("workflow") or ""), ""
    )
    entity = pack_entity(pack)
    if href_key:
        named = product_for(href_key, entity)
        if named:
            return named
    for item in pack.get("evidence") or []:
        facts = item.get("facts") if isinstance(item, dict) else {}
        if isinstance(facts, dict) and facts.get("product_id"):
            return str(facts["product_id"])
        if isinstance(facts, dict) and facts.get("product"):
            return str(facts["product"])
    return ""


def list_contradictions() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    href_map = {"batch_evidence": "batch", "pv_intake": "pv", "supply_options": "supply"}
    for request_id, pack in _PACKS.items():
        workflow = str(pack.get("workflow") or "pack")
        href_key = href_map.get(workflow, "batch")
        entity = pack_entity(pack)
        product = pack_product(pack)
        responses = list(_RESPONSES.get(request_id) or [])
        for item in pack.get("contradictions") or []:
            if not isinstance(item, dict):
                continue
            record_id = str(item.get("record_id") or "")
            topic = str(item.get("topic") or "")
            subject = record_id or topic
            follow_ups = [row for row in responses if str(row.get("subject_id") or "") in {subject, record_id, f"{record_id}:{topic}"}]
            left = item.get("left") if isinstance(item.get("left"), dict) else {}
            right = item.get("right") if isinstance(item.get("right"), dict) else {}
            rows.append(
                {
                    "request_id": request_id,
                    "workflow": workflow,
                    "product": product,
                    "entity": entity,
                    "topic": topic,
                    "record_id": record_id,
                    "source": str(item.get("source") or ""),
                    "statement": str(item.get("statement") or ""),
                    "values": list(item.get("values") or []),
                    "left": str(left.get("value") or item.get("statement") or ""),
                    "right": str(right.get("value") or item.get("topic") or ""),
                    "left_source": str(left.get("source") or item.get("source") or ""),
                    "right_source": str(right.get("source") or ""),
                    "href": f"/workflows/{href_key}/{entity}?request_id={request_id}",
                    "follow_ups": follow_ups,
                }
            )
    return rows


def list_sessions() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for request_id, pack in _PACKS.items():
        remaining = outstanding_critical(request_id)
        critical = critical_record_ids(pack)
        responses = list(_RESPONSES.get(request_id) or [])
        if any(item.get("event") == "acknowledge" for item in responses):
            review_state = "acknowledged"
        elif responses:
            review_state = "follow_up_recorded"
        elif remaining:
            review_state = "evidence_outstanding"
        else:
            review_state = "ready_for_acknowledgement"
        workflow = str(pack.get("workflow") or "pack")
        href_key = {"batch_evidence": "batch", "pv_intake": "pv", "supply_options": "supply"}.get(workflow, "batch")
        entity = pack_entity(pack)
        rows.append(
            {
                "request_id": request_id,
                "workflow": workflow,
                "entity": entity,
                "product": pack_product(pack),
                "href": f"/workflows/{href_key}/{entity}?request_id={request_id}",
                "remaining": remaining,
                "critical": critical,
                "review_state": review_state,
                "readiness_state": pack.get("readiness_state") or pack.get("execution_status"),
                "responses": responses,
            }
        )
    return rows


def _acknowledge(request_id: str, *, user: str, as_of: str, action_taken: str = "") -> dict[str, Any]:
    pack = _PACKS.get(request_id)
    if pack is None:
        return _error("SOURCE_UNAVAILABLE", "Pack is not loaded", request_id, as_of)
    preparer = _PREPARERS.get(request_id) or ""
    if preparer and preparer == user:
        write_audit(
            {
                "event": "acknowledge_refused",
                "request_id": request_id,
                "user": user,
                "reason": "segregation_of_duties",
            }
        )
        _persist_review(
            request_id,
            event="acknowledge_refused",
            user=user,
            reason="segregation_of_duties",
            session=False,
        )
        return _error("AUTHZ_DENIED", "Preparer cannot acknowledge the same pack", request_id, str(pack.get("as_of") or ""))
    remaining = outstanding_critical(request_id)
    if remaining:
        write_audit(
            {
                "event": "acknowledge_refused",
                "request_id": request_id,
                "user": user,
                "reason": "critical_evidence_unopened",
                "remaining": remaining,
            }
        )
        _persist_review(
            request_id,
            event="acknowledge_refused",
            user=user,
            reason="critical_evidence_unopened",
            action_taken=", ".join(remaining),
            session=False,
        )
        return _error(
            "AUTHZ_DENIED",
            "Critical evidence remains unopened: " + ", ".join(remaining),
            request_id,
            str(pack.get("as_of") or ""),
        )
    pack_hash = __import__("hashlib").sha256(dumps(pack)).hexdigest()
    write_audit(
        {
            "event": "acknowledge",
            "request_id": request_id,
            "user": user,
            "pack_hash": pack_hash,
            "as_of": str(pack.get("as_of") or as_of),
            "action_taken": action_taken,
            "signature": False,
            "disposition": False,
        }
    )
    stored = _store_response(
        request_id,
        event="acknowledge",
        user=user,
        action_taken=action_taken,
        pack_hash=pack_hash,
    )
    return _json_response(
        200,
        {
            "recorded": True,
            "signature": False,
            "disposition": False,
            "request_id": request_id,
            "evidence_seq": stored.get("seq"),
            "label": "Acknowledgement is a workflow event, not an electronic signature and not a disposition.",
        },
    )


def inventory() -> dict[str, Any]:
    return {
        "mutations": list(MUTATION_PATHS),
        "prohibited_tokens": list(PROHIBITED_ACTION_TOKENS),
    }
