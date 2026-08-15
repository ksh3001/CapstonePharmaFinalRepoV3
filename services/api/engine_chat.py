"""In-memory engine chat transcript. Presentation only. Not an evidence record."""

from __future__ import annotations

from typing import Any

_MAX = 24
_TURNS: list[dict[str, Any]] = []


def reset_chat() -> None:
    _TURNS.clear()


def turns() -> list[dict[str, Any]]:
    return list(_TURNS)


def record_turn(question: str, payload: dict[str, Any]) -> dict[str, Any]:
    text = (question or "").strip()
    facts = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    tool = str(payload.get("tool") or "")
    if not tool:
        if facts.get("seed") or "visited" in facts:
            tool = "get_graph_neighbourhood"
        elif payload.get("entity_id"):
            tool = "get_evidence_pack"
        elif "inject" in text.casefold():
            tool = "get_inject_coverage"
        else:
            tool = "ask"
    turn = {
        "question": text,
        "answer": str(payload.get("answer") or "No answer."),
        "ok": bool(payload.get("ok")),
        "entity_id": str(payload.get("entity_id") or ""),
        "tool": tool,
        "narrative": str(payload.get("narrative") or ""),
        "narrative_blocks": dict(payload.get("narrative_blocks") or {})
        if isinstance(payload.get("narrative_blocks"), dict)
        else {},
        "facts": facts,
    }
    _TURNS.append(turn)
    del _TURNS[:-_MAX]
    return turn
