"""Deny-list grader over rendered strings at any depth. The list may only grow."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DENY_LIST_PATH = HERE / "deny_list.json"
BASELINE_PATH = HERE / "deny_list.baseline.json"


class DenyListError(ValueError):
    """Pack text contained a prohibited phrase, or the deny-list was weakened."""


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def phrases() -> list[str]:
    payload = _load(DENY_LIST_PATH)
    return list(payload["phrases"])


def baseline_phrases() -> list[str]:
    payload = _load(BASELINE_PATH)
    return list(payload["phrases"])


def phrase_hash(values: list[str]) -> str:
    canonical = json.dumps({"phrases": sorted(values)}, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def assert_baseline() -> None:
    current = set(phrases())
    required = set(baseline_phrases())
    missing = sorted(required - current)
    if missing:
        raise DenyListError(
            "deny_list.json is missing baseline phrases (shrink is forbidden): " + ", ".join(missing)
        )
    recorded = _load(DENY_LIST_PATH).get("baseline_sha256", "")
    expected = phrase_hash(baseline_phrases())
    if recorded != expected:
        raise DenyListError("deny_list.json baseline_sha256 does not match the frozen baseline")


def _walk_strings(obj: Any) -> list[str]:
    found: list[str] = []
    if isinstance(obj, str):
        found.append(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            found.extend(_walk_strings(value))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_walk_strings(item))
    return found


def grade(pack: Any) -> list[str]:
    assert_baseline()
    hits: list[str] = []
    rendered = _walk_strings(pack)
    lowered = [item.lower() for item in rendered]
    for phrase in phrases():
        needle = phrase.lower()
        for index, text in enumerate(lowered):
            if needle in text:
                hits.append(f"{phrase!r} in {rendered[index]!r}")
    return hits


def assert_clean(pack: Any) -> None:
    hits = grade(pack)
    if hits:
        raise DenyListError("prohibited language: " + "; ".join(hits))
