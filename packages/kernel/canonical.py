"""Canonical JSON and derived identifiers (master plan §28)."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any, Iterable, Mapping, Sequence

ROUNDING = ROUND_HALF_EVEN


class FloatRejected(TypeError):
    """Binary floats are banned in packs (plan §28)."""


def _reject_floats(obj: Any, path: str = "$") -> None:
    if isinstance(obj, float) and not isinstance(obj, bool):
        raise FloatRejected(f"binary float at {path} is not serialisable")
    if isinstance(obj, Decimal):
        return
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            _reject_floats(value, f"{path}.{key}")
        return
    if isinstance(obj, (list, tuple)):
        for index, value in enumerate(obj):
            _reject_floats(value, f"{path}[{index}]")


def _default(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return format(obj, "f")
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serialisable")


def dumps(obj: Any) -> bytes:
    """Canonical JSON: sorted keys, no ASCII escape, compact separators, UTF-8, LF, trailing newline."""
    _reject_floats(obj)
    text = json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=_default,
    )
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.endswith("\n"):
        text += "\n"
    return text.encode("utf-8")


def sort_evidence(items: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(items, key=lambda item: (str(item.get("source", "")), str(item.get("record_id", ""))))


def sort_contradictions(items: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            str(item.get("topic", "")),
            str(item.get("source", "")),
            str(item.get("record_id", "")),
        ),
    )


def sort_gaps(items: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(items, key=lambda item: (str(item.get("gap_type", "")), str(item.get("subject_id", ""))))


def sort_abstentions(items: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(
        items,
        key=lambda item: (str(item.get("reason_code", "")), str(item.get("subject_id", ""))),
    )


def sort_findings(items: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(
        items,
        key=lambda item: (str(item.get("finding_id", "")), str(item.get("source", ""))),
    )


def derive_request_id(scenario_id: str, as_of: str, input_hash: str, code_version: str) -> str:
    material = f"{scenario_id}|{as_of}|{input_hash}|{code_version}".encode("utf-8")
    digest = hashlib.sha256(material).hexdigest()
    return f"REQ-{digest[:16]}"


def derived_timestamp(as_of: str) -> str:
    """retrieved_at / checked_at come from as_of, never the clock."""
    return as_of


def preserve_source_time(value: str) -> str:
    """Return the source timestamp unchanged, including precision and missing timezone."""
    return value


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Any) -> str:
    from pathlib import Path

    return sha256_bytes(Path(path).read_bytes())


def sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted(set(values))
