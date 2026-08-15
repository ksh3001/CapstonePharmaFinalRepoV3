"""UCUM validation. Invalid codes are reported, never repaired (BR-089)."""

from __future__ import annotations

KNOWN_UCUM = frozenset(
    {
        "mg/L",
        "ug/mL",
        "mg/mL",
        "%",
        "IU/mL",
        "Cel",
        "1",
    }
)


def ucum_valid(code: str) -> bool:
    text = (code or "").strip()
    if not text:
        return False
    return text in KNOWN_UCUM
