from __future__ import annotations

import json
import unittest

from packages.domain.graph_findings import recurrence_candidates
from packages.graph.projection import Projection, sample_provenance


class RecurrenceLinkageTests(unittest.TestCase):
    def test_candidates_across_taxonomy_labels_have_no_effectiveness_verdict(self) -> None:
        deviations = [
            {"deviation_id": "DEV-201", "taxonomy": "mixing_time", "status": "closed", "capa": "CAPA-31", "similarity_to": ""},
            {
                "deviation_id": "DEV-244",
                "taxonomy": "process_duration",
                "status": "open",
                "capa": "",
                "similarity_to": "DEV-201",
            },
        ]
        capa = {
            "capa_id": "CAPA-31",
            "action": "operator retraining",
            "effectiveness_check": "no recurrence under code mixing_time",
            "result": "effective",
        }
        candidates = recurrence_candidates(deviations)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["kind"], "POSSIBLY_RELATED_TO")
        self.assertEqual(set(candidates[0]["taxonomies"]), {"mixing_time", "process_duration"})
        self.assertEqual(candidates[0]["basis"], "similarity_to")
        graph = Projection()
        graph.add_node("DEV-201", "deviation", sample_provenance("DEV-201"))
        graph.add_node("DEV-244", "deviation", sample_provenance("DEV-244"))
        graph.add_edge("DEV-244", "DEV-201", "POSSIBLY_RELATED_TO", sample_provenance("link"))
        body = {"candidates": candidates, "edges": [edge.kind for edge in graph.edges()]}
        rendered = json.dumps(body).lower()
        self.assertNotIn("effective", rendered)
        self.assertNotIn("effectiveness", rendered)
        self.assertNotIn("closed", rendered)
        self.assertNotIn(capa["result"], json.dumps(body))
