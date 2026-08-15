"""Output guards G-1…G-5. Must not import domain logic."""

from __future__ import annotations

import json
import re
from typing import Any

from packages.contracts.deny import grade

NUMBER = re.compile(r"\d+(?:\.\d+)?")


def _as_dict(advice: Any) -> dict[str, Any]:
    if isinstance(advice, dict):
        return advice
    return {"text": str(advice or "")}


def guard_advice(pack: dict[str, Any], advice: Any) -> dict[str, Any]:
    payload = _as_dict(advice)
    extra = set(payload) - {"text", "evidence_refs", "labelled"}
    if extra:
        return {"passed": False, "check": "G-4", "reason": "additional_properties", "advice": None}
    text = str(payload.get("text") or "")
    hits = grade({"text": text})
    if hits:
        return {"passed": False, "check": "G-1", "reason": hits[0], "advice": None}
    refs = list(payload.get("evidence_refs") or [])
    known = {str(item.get("record_id") or "") for item in pack.get("evidence") or []}
    for ref in refs:
        if str(ref) not in known:
            return {"passed": False, "check": "G-2", "reason": f"missing_citation:{ref}", "advice": None}
    rendered_pack = json.dumps(pack)
    for match in NUMBER.findall(text):
        if match not in rendered_pack:
            return {"passed": False, "check": "G-3", "reason": f"unverified_number:{match}", "advice": None}
    abstentions = pack.get("abstentions") or []
    if abstentions:
        lowered = text.casefold()
        if any(token in lowered for token in ("therefore the case is", "so the batch is", "resolved", "no issue remains")):
            return {"passed": False, "check": "G-5", "reason": "narrates_past_abstention", "advice": None}
    labelled = dict(payload)
    labelled["labelled"] = "model-generated"
    labelled["text"] = text
    return {"passed": True, "check": "all", "advice": labelled}
