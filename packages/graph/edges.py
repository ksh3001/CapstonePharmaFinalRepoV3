"""Edge type registry. Forbidden types are unrepresentable (plan §5.4)."""

from __future__ import annotations

PERMITTED_EDGES = frozenset(
    {
        "DERIVED_FROM",
        "CONSUMED",
        "TESTED_BY",
        "DOCUMENTED_BY",
        "MONITORED_BY",
        "AGGREGATED_INTO",
        "SHIPPED_IN",
        "REPORTED_IN",
        "CODED_AS",
        "SUPERSEDES",
        "REFERENCES",
        "DUPLICATE_CANDIDATE_OF",
        "POSSIBLY_RELATED_TO",
    }
)

FORBIDDEN_EDGES = frozenset(
    {
        "RESERVED_FOR",
        "ALLOCATED_TO",
        "SHIPPED_AS",
        "DISPOSITION_SET",
        "RELEASED",
        "SIGNAL_CONFIRMED",
        "ELIGIBILITY_DECIDED",
        "RECALL_INITIATED",
    }
)

# Citation edges may point at untrusted documents. They never ground a decision.
CITATION_EDGES = frozenset({"DOCUMENTED_BY", "REFERENCES"})


class ForbiddenEdgeError(ValueError):
    """An edge type the system is not allowed to represent."""


def assert_edge_type(kind: str) -> None:
    if kind in FORBIDDEN_EDGES or kind not in PERMITTED_EDGES:
        raise ForbiddenEdgeError(kind)
