from __future__ import annotations

import unittest

from packages.graph.builder import build_projection, graph_summary, seed_for
from packages.graph.edges import FORBIDDEN_EDGES, ForbiddenEdgeError
from packages.kernel.canonical import dumps
from packages.kernel.checkpoint import reset_replay
from packages.orchestrator.deterministic import StdlibOrchestrator
from tests.helpers import load_pub

AS_OF = "2026-08-01T08:00:00Z"


class GraphBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()
        self.graph = build_projection(as_of=AS_OF)

    def test_both_batch_ids_are_nodes(self) -> None:
        ids = set(self.graph.node_ids())
        self.assertIn("batches.csv:NCB204-B24071", ids)
        self.assertIn("batches.csv:NCS310-S26033", ids)

    def test_consumed_genealogy_is_linked_from_the_batch(self) -> None:
        seed = "batches.csv:NCB204-B24071"
        walked = self.graph.traverse(seed, as_of=AS_OF)
        self.assertIn("material_genealogy.csv:RESIN-R44", walked.visited)
        kinds = {(edge.target, edge.kind) for edge in self.graph.edges() if edge.source == seed}
        self.assertIn(("material_genealogy.csv:RESIN-R44", "CONSUMED"), kinds)
        self.assertIn(("material_genealogy.csv:SUA-88", "REFERENCES"), kinds)

    def test_lab_result_and_missing_parent_files_do_not_fail_the_build(self) -> None:
        walked = self.graph.traverse("batches.csv:NCB204-B24071", as_of=AS_OF)
        self.assertIn("lab_results.csv:LR-88", walked.visited)
        self.assertGreater(len(self.graph.node_ids()), 20)
        self.assertGreater(len(self.graph.edges()), 10)

    def test_duplicate_candidates_link_both_cases(self) -> None:
        seed = seed_for(self.graph, "PV-1001")
        self.assertEqual(seed, "icsr_cases.csv:PV-1001")
        walked = self.graph.traverse(seed, as_of=AS_OF)
        self.assertIn("icsr_cases.csv:PV-1014", walked.visited)
        self.assertIn("icsr_cases.csv:PV-1009", walked.visited)

    def test_shipment_reaches_logger_readings(self) -> None:
        seed = seed_for(self.graph, "SH-901")
        self.assertEqual(seed, "shipments.csv:SH-901")
        walked = self.graph.traverse(seed, as_of=AS_OF)
        logger_nodes = [node_id for node_id in walked.visited if node_id.startswith("temperature_loggers.csv:LG-31")]
        self.assertTrue(logger_nodes)

    def test_second_batch_is_a_separate_seed(self) -> None:
        walked = self.graph.traverse("batches.csv:NCS310-S26033", as_of=AS_OF)
        self.assertIn("material_genealogy.csv:VIAL-V19", walked.visited)
        self.assertNotIn("batches.csv:NCB204-B24071", walked.visited)

    def test_forbidden_edge_still_raises(self) -> None:
        for kind in sorted(FORBIDDEN_EDGES):
            with self.subTest(kind=kind):
                with self.assertRaises(ForbiddenEdgeError):
                    self.graph.add_edge(
                        "batches.csv:NCB204-B24071",
                        "batches.csv:NCS310-S26033",
                        kind,
                        self.graph.node("batches.csv:NCB204-B24071").provenance,
                    )

    def test_summary_is_deterministic(self) -> None:
        first = graph_summary(self.graph, "NCB204-B24071", as_of=AS_OF)
        second = graph_summary(build_projection(as_of=AS_OF), "NCB204-B24071", as_of=AS_OF)
        self.assertEqual(dumps(first), dumps(second))
        self.assertEqual(first["store"], "in_process")
        self.assertEqual(first["source"], "data/RELATIONSHIP_MODEL.csv")
        self.assertEqual(first["seed"], "batches.csv:NCB204-B24071")

    def test_orchestrated_pack_carries_projection_on_human_review(self) -> None:
        pack = StdlibOrchestrator().run(
            {"fixture": load_pub("PUB-01"), "workflow": "batch", "entity_id": "NCB204-B24071"}
        )
        projection = pack["human_review"]["graph_projection"]
        self.assertEqual(projection["store"], "in_process")
        self.assertIn("batches.csv:NCB204-B24071", projection["visited"])
        self.assertNotIn("graph", pack)
        self.assertEqual(
            dumps(pack["human_review"]["graph_projection"]),
            dumps(
                StdlibOrchestrator()
                .run({"fixture": load_pub("PUB-01"), "workflow": "batch", "entity_id": "NCB204-B24071"})[
                    "human_review"
                ]["graph_projection"]
            ),
        )
