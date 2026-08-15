"""Model restatement of an already-computed tool result. The model does not choose a tool."""

from __future__ import annotations

from typing import Any


def narrate_tool_result(question: str, payload: dict[str, Any]) -> str:
    blocks = narrate_tool_blocks(question, payload)
    return " ".join(part for part in (blocks.get("headline"), blocks.get("meaning")) if part)


def narrate_tool_blocks(question: str, payload: dict[str, Any]) -> dict[str, str]:
    if not payload.get("ok"):
        return {}
    from services.integration.azure.openai import summarize_tool_blocks

    return summarize_tool_blocks(payload, question=question)
