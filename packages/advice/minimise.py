"""Prompt minimisation before any model call (BR-106). Does not import kernel (tier)."""

from __future__ import annotations

from typing import Any

from packages.ontology.instructions import contains_embedded_instruction

DIRECT_ID_KEYS = frozenset({"patient_key", "patient_id", "initials", "date_of_birth", "dob", "name", "email"})


def minimise_pack(pack: dict[str, Any], *, role_id: str | None = None) -> dict[str, Any]:
    del role_id
    return _drop_direct(pack)


def _drop_direct(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            if key in DIRECT_ID_KEYS:
                out[key] = "PN-redacted"
            else:
                out[key] = _drop_direct(value)
        return out
    if isinstance(obj, list):
        return [_drop_direct(item) for item in obj]
    if isinstance(obj, str) and contains_embedded_instruction(obj):
        return "UNTRUSTED_INSTRUCTION_REDACTED"
    return obj
