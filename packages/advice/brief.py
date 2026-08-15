"""Evidence-only prompt body for advisory notes. No classification."""

from __future__ import annotations

from typing import Any


def _rows(pack: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return [item for item in (pack.get(key) or []) if isinstance(item, dict)]


def evidence_brief(pack: dict[str, Any]) -> dict[str, Any]:
    evidence = []
    for item in _rows(pack, "evidence"):
        row: dict[str, Any] = {
            "record_id": item.get("record_id"),
            "source": item.get("source"),
            "authority": item.get("authority"),
        }
        facts = item.get("facts")
        if isinstance(facts, dict) and facts:
            row["facts"] = facts
        evidence.append(row)
    contradictions = []
    for item in _rows(pack, "contradictions"):
        contradictions.append(
            {
                "topic": item.get("topic"),
                "record_id": item.get("record_id"),
                "values": list(item.get("values") or []),
                "statement": item.get("statement"),
            }
        )
    gaps = []
    for item in _rows(pack, "gaps"):
        gaps.append(
            {
                "gap_type": item.get("gap_type"),
                "packet_item": item.get("packet_item"),
                "subject_id": item.get("subject_id"),
                "record_id": item.get("record_id"),
            }
        )
    abstentions = []
    for item in _rows(pack, "abstentions"):
        abstentions.append(
            {
                "reason_code": item.get("reason_code") or item.get("code"),
                "subject_id": item.get("subject_id"),
                "observed": item.get("observed"),
                "specified": item.get("specified"),
            }
        )
    entity = {
        key: pack.get(key)
        for key in ("batch_id", "case_ids", "event_id", "workflow", "readiness_state")
        if pack.get(key)
    }
    return {
        "instruction": (
            "Write a short evidence-based summary for a human reviewer. "
            "Use only the evidence, contradictions, gaps, and abstentions below. "
            "Cite record_id values that appear in evidence. "
            "Do not decide, approve, release, reject, allocate, ship, recall, or sign."
        ),
        "entity": entity,
        "evidence": evidence,
        "contradictions": contradictions,
        "gaps": gaps,
        "abstentions": abstentions,
    }


def stub_advice(pack: dict[str, Any]) -> dict[str, Any]:
    refs = [
        str(item.get("record_id") or "")
        for item in _rows(pack, "evidence")
        if item.get("record_id")
    ]
    parts = ["Model-generated summary of the pack."]
    if refs:
        parts.append("Evidence records to inspect: " + ", ".join(refs) + ".")
    gap_labels = []
    for item in _rows(pack, "gaps"):
        kind = str(item.get("gap_type") or "")
        packet = str(item.get("packet_item") or "")
        label = " ".join(part for part in (kind, packet) if part)
        if label:
            gap_labels.append(label)
    if gap_labels:
        parts.append("Gaps: " + "; ".join(gap_labels) + ".")
    topics = []
    for item in _rows(pack, "contradictions"):
        topic = str(item.get("topic") or "")
        if topic:
            topics.append(topic)
    if topics:
        parts.append("Contradictions: " + "; ".join(topics) + ".")
    reasons = []
    for item in _rows(pack, "abstentions"):
        reason = str(item.get("reason_code") or item.get("code") or "")
        if reason:
            reasons.append(reason)
    if reasons:
        parts.append("Abstentions: " + "; ".join(reasons) + ".")
    parts.append("Inspect the cited evidence before recording action taken.")
    return {
        "text": " ".join(parts),
        "evidence_refs": list(refs),
        "labelled": "model-generated",
    }
