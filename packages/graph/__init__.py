"""In-process knowledge-graph projection. Stdlib property graph (TASK-015)."""

from packages.graph.builder import build_projection, graph_summary, seed_for
from packages.graph.edges import FORBIDDEN_EDGES, PERMITTED_EDGES, ForbiddenEdgeError, assert_edge_type
from packages.graph.projection import HARD_CAP, Projection, sample_provenance
from packages.graph.types import Edge, Node, Provenance, TraversalResult

__all__ = [
    "FORBIDDEN_EDGES",
    "HARD_CAP",
    "PERMITTED_EDGES",
    "Edge",
    "ForbiddenEdgeError",
    "Node",
    "Projection",
    "Provenance",
    "TraversalResult",
    "assert_edge_type",
    "build_projection",
    "graph_summary",
    "sample_provenance",
    "seed_for",
]
