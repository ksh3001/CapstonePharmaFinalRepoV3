"""Core ontology value types. These describe disagreement; they never resolve it."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TrustStatus = Literal[
    "trusted",
    "untrusted",
    "referenced_missing",
    "superseded",
    "reduced_integrity",
]

IdentityVerdict = Literal["SAME", "SAME_BY_MAPPING", "RELATED", "IdentityConflict"]

TimeBasis = Literal["event_time", "recorded_at"]

NON_GROUNDING_TRUST: frozenset[str] = frozenset(
    {"untrusted", "referenced_missing", "superseded", "reduced_integrity"}
)
BLOCKING_MAPPING_STATUS: frozenset[str] = frozenset(
    {
        "proposed",
        "draft",
        "superseded",
        "ambiguous",
        "ambiguous_strength_presentation",
        "no",
        "false",
    }
)


@dataclass(frozen=True)
class Identifier:
    scheme: str
    value: str
    org_namespace: str


@dataclass(frozen=True)
class Quantity:
    value: str
    unit_code: str
    unit_system: str
    mapping_id: str | None = None


@dataclass(frozen=True)
class TimePoint:
    value: str
    precision: str
    timezone_known: bool
    basis: TimeBasis


@dataclass(frozen=True)
class Authority:
    document_id: str
    status: str
    effective_from: str
    effective_to: str | None = None
    jurisdiction: str | None = None


@dataclass(frozen=True)
class Coding:
    term: str
    dictionary: str
    version: str


@dataclass(frozen=True)
class Measurement:
    value: str
    unit_code: str
    method: str
    method_version: str


@dataclass(frozen=True)
class ComparisonResult:
    comparable: bool
    reason_code: str | None = None
    mapping_id: str | None = None
    converted_value: None = None


@dataclass(frozen=True)
class IdentityResult:
    verdict: IdentityVerdict
    mapping_id: str | None = None
    reason_code: str | None = None


@dataclass(frozen=True)
class BackEntryFlag:
    flagged: bool
    event_time: str
    recorded_at: str
    magnitude: str
