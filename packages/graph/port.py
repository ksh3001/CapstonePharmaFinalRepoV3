"""GraphPort: engines depend on this, not on a store (plan §5.3)."""

from __future__ import annotations

from typing import Protocol

from packages.graph.types import Edge, Node, Provenance, TraversalResult
from packages.ontology.types import TrustStatus


class GraphPort(Protocol):
    def add_node(
        self,
        node_id: str,
        kind: str,
        provenance: Provenance,
        *,
        trust_status: TrustStatus = "trusted",
        facts: dict | None = None,
    ) -> Node: ...

    def add_edge(self, source: str, target: str, kind: str, provenance: Provenance) -> Edge: ...

    def traverse(
        self,
        seed: str,
        *,
        max_hops: int = 4,
        as_of: str = "",
        allowed: frozenset[str] | None = None,
    ) -> TraversalResult: ...
