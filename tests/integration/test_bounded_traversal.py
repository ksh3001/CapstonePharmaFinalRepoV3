from __future__ import annotations

import unittest

from packages.domain.graph_findings import traverse_recall_scope
from packages.graph.projection import HARD_CAP, Projection, sample_provenance


def _chain(length: int) -> Projection:
    graph = Projection()
    for index in range(length):
        node_id = f"n{index}"
        graph.add_node(node_id, "lot", sample_provenance(node_id))
        if index:
            graph.add_edge(f"n{index - 1}", node_id, "POSSIBLY_RELATED_TO", sample_provenance(f"e{index}"))
    return graph


class BoundedTraversalTests(unittest.TestCase):
    def test_seven_hop_chain_is_incomplete_at_default_depth(self) -> None:
        graph = _chain(8)
        result, abstention = traverse_recall_scope(graph, "n0", max_hops=4)
        self.assertTrue(result.traversal_incomplete)
        self.assertIn("n5", result.frontier)
        self.assertNotIn("n7", result.visited)
        self.assertIsNotNone(abstention)
        assert abstention is not None
        self.assertEqual(abstention.reason_code, "traversal_incomplete")
        self.assertIn("n5", abstention.extra["frontier"])

    def test_hard_cap_is_six(self) -> None:
        graph = _chain(8)
        result, abstention = traverse_recall_scope(graph, "n0", max_hops=99)
        self.assertEqual(result.max_hops, HARD_CAP)
        self.assertTrue(result.traversal_incomplete)
        self.assertIn("n6", result.visited)
        self.assertIn("n7", result.frontier)
        self.assertIsNotNone(abstention)

    def test_short_path_is_complete(self) -> None:
        graph = _chain(3)
        result, abstention = traverse_recall_scope(graph, "n0", max_hops=4)
        self.assertFalse(result.traversal_incomplete)
        self.assertEqual(result.frontier, ())
        self.assertIsNone(abstention)
        self.assertEqual(set(result.visited), {"n0", "n1", "n2"})
