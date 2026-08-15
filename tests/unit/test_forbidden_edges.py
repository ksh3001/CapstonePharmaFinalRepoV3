from __future__ import annotations

import unittest

from packages.graph.edges import FORBIDDEN_EDGES, ForbiddenEdgeError, assert_edge_type
from packages.graph.projection import OrphanEdgeError, Projection, UngroundedEdgeError, sample_provenance


class ForbiddenEdgeTests(unittest.TestCase):
    def test_each_forbidden_label_raises(self) -> None:
        graph = Projection()
        graph.add_node("a", "batch", sample_provenance("a"))
        graph.add_node("b", "lot", sample_provenance("b"))
        for kind in sorted(FORBIDDEN_EDGES):
            with self.subTest(kind=kind):
                with self.assertRaises(ForbiddenEdgeError) as ctx:
                    graph.add_edge("a", "b", kind, sample_provenance(kind))
                self.assertIn(kind, str(ctx.exception))

    def test_same_as_is_unrepresentable(self) -> None:
        with self.assertRaises(ForbiddenEdgeError):
            assert_edge_type("SAME_AS")
        with self.assertRaises(ForbiddenEdgeError):
            assert_edge_type("MERGED_INTO")

    def test_permitted_consumed_is_accepted(self) -> None:
        graph = Projection()
        graph.add_node("batch:1", "batch", sample_provenance("batch:1"))
        graph.add_node("lot:1", "lot", sample_provenance("lot:1"))
        edge = graph.add_edge("batch:1", "lot:1", "CONSUMED", sample_provenance("e1"))
        self.assertEqual(edge.kind, "CONSUMED")

    def test_orphan_edge_is_rejected(self) -> None:
        graph = Projection()
        graph.add_node("a", "batch", sample_provenance("a"))
        with self.assertRaises(OrphanEdgeError):
            graph.add_edge("a", "missing", "CONSUMED", sample_provenance("e"))

    def test_missing_provenance_is_rejected(self) -> None:
        from packages.graph.types import Provenance

        with self.assertRaises(ValueError):
            Provenance(
                source_system="",
                record_id="x",
                authority="challenge-package",
                effective_time=None,
                retrieved_at="2026-08-01T08:00:00Z",
                sha256="a" * 64,
            )

    def test_untrusted_node_cannot_source_an_edge(self) -> None:
        graph = Projection()
        graph.add_node("doc", "document", sample_provenance("doc"), trust_status="untrusted")
        graph.add_node("batch", "batch", sample_provenance("batch"))
        with self.assertRaises(UngroundedEdgeError):
            graph.add_edge("doc", "batch", "DERIVED_FROM", sample_provenance("e"))
        graph.add_edge("batch", "doc", "DOCUMENTED_BY", sample_provenance("cite"))
