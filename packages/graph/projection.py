"""In-process property graph. Rebuilt per run; never a system of record."""

from __future__ import annotations

from collections import deque
from typing import Any

from packages.graph.edges import assert_edge_type
from packages.graph.types import Edge, Node, Provenance, TraversalResult
from packages.ontology.trust import can_ground_assertion
from packages.ontology.types import TrustStatus

DEFAULT_HOPS = 4
HARD_CAP = 6


class OrphanEdgeError(ValueError):
    """An edge referenced a node that is not in the projection."""


class UngroundedEdgeError(ValueError):
    """Untrusted content cannot source a grounding edge (plan §5.4)."""


class Projection:
    """Stdlib adjacency-dict graph implementing GraphPort."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._out: dict[str, list[Edge]] = {}
        self._edges: list[Edge] = []

    def add_node(
        self,
        node_id: str,
        kind: str,
        provenance: Provenance,
        *,
        trust_status: TrustStatus = "trusted",
        facts: dict[str, Any] | None = None,
    ) -> Node:
        node = Node(
            node_id=node_id,
            kind=kind,
            provenance=provenance,
            trust_status=trust_status,
            facts=dict(facts or {}),
        )
        self._nodes[node_id] = node
        self._out.setdefault(node_id, [])
        return node

    def add_edge(self, source: str, target: str, kind: str, provenance: Provenance) -> Edge:
        assert_edge_type(kind)
        if source not in self._nodes or target not in self._nodes:
            raise OrphanEdgeError(f"{kind} {source}->{target}")
        src = self._nodes[source]
        if not can_ground_assertion(src.trust_status):
            raise UngroundedEdgeError(f"{kind} from {source} ({src.trust_status})")
        edge = Edge(source=source, target=target, kind=kind, provenance=provenance)
        self._out[source].append(edge)
        self._edges.append(edge)
        return edge

    def node(self, node_id: str) -> Node:
        return self._nodes[node_id]

    def node_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._nodes))

    def edges(self) -> tuple[Edge, ...]:
        return tuple(
            sorted(self._edges, key=lambda item: (item.source, item.kind, item.target, item.provenance.record_id))
        )

    def traverse(
        self,
        seed: str,
        *,
        max_hops: int = DEFAULT_HOPS,
        as_of: str = "",
        allowed: frozenset[str] | None = None,
    ) -> TraversalResult:
        hops = min(max(max_hops, 0), HARD_CAP)
        if seed not in self._nodes:
            return TraversalResult(
                seed=seed,
                visited=(),
                frontier=(),
                traversal_incomplete=True,
                hops_used=0,
                max_hops=hops,
            )
        if allowed is not None and seed not in allowed:
            return TraversalResult(
                seed=seed,
                visited=(),
                frontier=(),
                traversal_incomplete=True,
                hops_used=0,
                max_hops=hops,
            )
        visited: dict[str, int] = {seed: 0}
        queue: deque[tuple[str, int]] = deque([(seed, 0)])
        frontier: list[str] = []
        while queue:
            current, depth = queue.popleft()
            if depth >= hops:
                for edge in self._out.get(current, ()):
                    if not self._edge_usable(edge, as_of=as_of, allowed=allowed):
                        continue
                    if edge.target not in visited and edge.target not in frontier:
                        frontier.append(edge.target)
                continue
            for edge in self._out.get(current, ()):
                if not self._edge_usable(edge, as_of=as_of, allowed=allowed):
                    continue
                nxt = edge.target
                if nxt in visited:
                    continue
                visited[nxt] = depth + 1
                queue.append((nxt, depth + 1))
        incomplete = bool(frontier)
        ordered = tuple(sorted(visited, key=lambda item: (visited[item], item)))
        frontier_ids = tuple(sorted(set(frontier)))
        hops_used = max(visited.values()) if visited else 0
        return TraversalResult(
            seed=seed,
            visited=ordered,
            frontier=frontier_ids,
            traversal_incomplete=incomplete,
            hops_used=hops_used,
            max_hops=hops,
        )

    def _edge_usable(self, edge: Edge, *, as_of: str, allowed: frozenset[str] | None) -> bool:
        if allowed is not None and edge.target not in allowed:
            return False
        effective = edge.provenance.effective_time or ""
        if as_of and effective and effective > as_of:
            return False
        return True


def sample_provenance(record_id: str, source_system: str = "test") -> Provenance:
    return Provenance(
        source_system=source_system,
        record_id=record_id,
        authority="challenge-package",
        effective_time="2026-07-01",
        retrieved_at="2026-08-01T08:00:00Z",
        sha256="a" * 64,
        source_preserved=True,
    )


__all__ = [
    "DEFAULT_HOPS",
    "HARD_CAP",
    "OrphanEdgeError",
    "Projection",
    "UngroundedEdgeError",
    "sample_provenance",
]
