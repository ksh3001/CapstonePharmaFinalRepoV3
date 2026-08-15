"""Graph value types. The projection is rebuilt every run; nothing here is stored."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from packages.ontology.types import TrustStatus


@dataclass(frozen=True)
class Provenance:
    source_system: str
    record_id: str
    authority: str
    effective_time: str | None
    retrieved_at: str
    sha256: str
    source_preserved: bool = True

    def __post_init__(self) -> None:
        if not self.source_system or not self.record_id or not self.authority or not self.retrieved_at:
            raise ValueError("provenance requires source_system, record_id, authority, retrieved_at")
        if not self.sha256:
            raise ValueError("provenance requires integrity sha256")
        if self.source_preserved is not True:
            raise ValueError("provenance.source_preserved must be true")


@dataclass(frozen=True)
class Node:
    node_id: str
    kind: str
    provenance: Provenance
    trust_status: TrustStatus = "trusted"
    facts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    kind: str
    provenance: Provenance


@dataclass(frozen=True)
class TraversalResult:
    seed: str
    visited: tuple[str, ...]
    frontier: tuple[str, ...]
    traversal_incomplete: bool
    hops_used: int
    max_hops: int
