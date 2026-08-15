"""Embedded-instruction scanner. Retrieved text is data (BR-009, BR-035, INJ-065)."""

from __future__ import annotations

import re
from typing import Any

# Closed list. Patterns are injection/imperative-to-the-system, not ordinary procedure language.
# "Ignore embedded instructions that request bypass of controls" must not match.
_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_previous_instructions", re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE)),
    ("disregard_previous_instructions", re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE)),
    ("ignore_quality_holds", re.compile(r"ignore\s+all\s+quality\s+holds", re.IGNORECASE)),
    ("mark_batch_ready", re.compile(r"mark\s+the\s+batch\s+ready", re.IGNORECASE)),
    ("hidden_instruction", re.compile(r"hidden\s+instruction\s*:", re.IGNORECASE)),
    ("reader_must_act", re.compile(r"the\s+reader\s+(must|shall)\b", re.IGNORECASE)),
    ("take_the_following_action", re.compile(r"take\s+the\s+following\s+action", re.IGNORECASE)),
    ("enroll_the_subject_now", re.compile(r"enroll\s+the\s+subject\s+now", re.IGNORECASE)),
)


def matched_instruction_rules(text: str) -> tuple[str, ...]:
    if not text:
        return ()
    return tuple(name for name, pattern in _RULES if pattern.search(text))


def contains_embedded_instruction(text: str) -> bool:
    return bool(matched_instruction_rules(text))


def flatten_strings(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return "\n".join(flatten_strings(value) for value in obj.values())
    if isinstance(obj, list):
        return "\n".join(flatten_strings(item) for item in obj)
    return ""


def facts_excluding_instructions(record: dict[str, Any]) -> dict[str, Any]:
    """Drop fields whose verbatim value is an embedded instruction. Never copy the payload forward."""
    clean: dict[str, Any] = {}
    for key, value in record.items():
        if isinstance(value, str) and contains_embedded_instruction(value):
            continue
        clean[key] = value
    return clean
