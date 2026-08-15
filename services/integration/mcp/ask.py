"""Deterministic question router over read-only engine tools. The model does not choose a step."""

from __future__ import annotations

import re
from typing import Any

from packages.config.catalog import find_in_text
from services.integration.mcp.narrate import narrate_tool_blocks
from services.integration.mcp.tools import call_tool

_DECIDE = (
    "release the batch",
    "dispose",
    "allocate stock",
    "initiate a recall",
    "merge the cases",
)
_GRAPH = re.compile(
    r"\b(linked|related|relation|neighbourhood|neighborhood|neighbours?|neighbors?|"
    r"connected|graph|hops)\b",
    re.IGNORECASE,
)
_HELP = (
    "Pack chat answers pack status or the relation-graph neighbourhood for a catalog id "
    "such as NCB204-B24071, PV-1001, or SH-901. It does not answer general questions. "
    "Try: What is the status of NCB204-B24071? or What is linked to NCB204-B24071?"
)


def _mentions_decide(text: str) -> bool:
    blob = text.casefold()
    return any(phrase in blob for phrase in _DECIDE)


def _mentions_graph(text: str) -> bool:
    return _GRAPH.search(text or "") is not None


def _format_summary(summary: dict[str, Any]) -> str:
    remaining = summary.get("remaining_critical") or []
    leftover = ", ".join(str(item) for item in remaining[:6]) or "none"
    product = str(summary.get("product") or "").strip()
    product_bit = f", product {product}" if product else ""
    return (
        f"{summary.get('entity') or 'Pack'} "
        f"({summary.get('workflow') or 'workflow'}{product_bit}). "
        f"Readiness {summary.get('readiness_state') or 'unknown'}. "
        f"Execution {summary.get('execution_status') or 'unknown'}. "
        f"Findings {summary.get('findings')}, contradictions {summary.get('contradictions')}, "
        f"gaps {summary.get('gaps')}, abstentions {summary.get('abstentions')}. "
        f"Remaining critical evidence: {leftover}. "
        "Advisory only. The engine does not dispose, allocate, or certify."
    )


def _format_neighbourhood(summary: dict[str, Any]) -> str:
    visited = [str(item) for item in (summary.get("visited") or []) if item]
    shown = ", ".join(item.rsplit(":", 1)[-1] for item in visited[:6]) or "none"
    incomplete = (
        " Traversal stopped at the hop cap; the frontier is listed, not guessed."
        if summary.get("traversal_incomplete")
        else ""
    )
    return (
        f"{summary.get('entity') or 'Pack'} relation graph from "
        f"{summary.get('source') or 'data/RELATIONSHIP_MODEL.csv'}. "
        f"Seed {summary.get('seed') or 'none'}. "
        f"{summary.get('hops_used')}/{summary.get('max_hops')} hops. "
        f"{summary.get('visited_count')} nodes visited including {shown}."
        f"{incomplete} "
        "Advisory only. Not a system of record."
    )


def _attach_narrative(question: str, payload: dict[str, Any]) -> dict[str, Any]:
    blocks = narrate_tool_blocks(question, payload)
    payload["narrative_blocks"] = blocks
    payload["narrative"] = " ".join(
        part for part in (blocks.get("headline"), blocks.get("meaning")) if part
    )
    return payload


def answer_question(question: str, *, user: str) -> dict[str, Any]:
    text = (question or "").strip()
    if not text:
        return {"ok": False, "answer": _HELP, "advisory": True, "tool": "ask"}
    if _mentions_decide(text):
        return {
            "ok": False,
            "answer": "The engine does not decide. Open the pack and record a follow-up. No disposition here.",
            "advisory": True,
            "tool": "ask",
        }
    hit = find_in_text(text)
    if hit is not None and _mentions_graph(text):
        result = call_tool(
            "get_graph_neighbourhood",
            {"entity_id": hit.entity_id, "workflow": hit.workflow},
            user=user,
        )
        if not result.get("ok"):
            return {
                "ok": False,
                "answer": "The engine could not load that relation graph.",
                "entity_id": hit.entity_id,
                "error": result.get("error"),
                "advisory": True,
                "tool": "get_graph_neighbourhood",
            }
        summary = result.get("summary") or {}
        payload = {
            "ok": True,
            "answer": _format_neighbourhood(summary),
            "entity_id": hit.entity_id,
            "workflow": hit.workflow,
            "summary": summary,
            "advisory": True,
            "disposition": False,
            "tool": "get_graph_neighbourhood",
        }
        return _attach_narrative(text, payload)
    if hit is not None:
        result = call_tool(
            "get_evidence_pack",
            {"entity_id": hit.entity_id, "workflow": hit.workflow},
            user=user,
        )
        if not result.get("ok"):
            return {
                "ok": False,
                "answer": "The engine could not load that id.",
                "entity_id": hit.entity_id,
                "error": result.get("error"),
                "advisory": True,
                "tool": "get_evidence_pack",
            }
        summary = result.get("summary") or {}
        payload = {
            "ok": True,
            "answer": _format_summary(summary),
            "entity_id": hit.entity_id,
            "workflow": hit.workflow,
            "summary": summary,
            "advisory": True,
            "disposition": False,
            "tool": "get_evidence_pack",
        }
        return _attach_narrative(text, payload)
    if "inject" in text.casefold():
        result = call_tool("get_inject_coverage", {}, user=user)
        counts = (result.get("counts") or {}) if result.get("ok") else {}
        payload = {
            "ok": bool(result.get("ok")),
            "answer": (
                f"Inject coverage: {counts.get('covered', 0)} by rule, "
                f"{counts.get('artefact', 0)} artefact, {counts.get('uncovered', 0)} not covered."
            ),
            "counts": counts,
            "advisory": True,
            "tool": "get_inject_coverage",
        }
        if payload["ok"]:
            return _attach_narrative(text, payload)
        return payload
    if _mentions_graph(text):
        return {
            "ok": False,
            "answer": (
                "Name a catalog id for the relation graph, such as NCB204-B24071, PV-1001, or SH-901."
            ),
            "advisory": True,
            "tool": "ask",
        }
    return {"ok": False, "answer": _HELP, "advisory": True, "tool": "ask"}
