from __future__ import annotations

import unittest

from services.api.console import render_pack_page


class PackViewTests(unittest.TestCase):
    def test_gap_shows_packet_item_and_type(self) -> None:
        html = render_pack_page(
            {
                "request_id": "REQ-x",
                "findings": [],
                "gaps": [
                    {
                        "gap_type": "cmo_commitment_missing",
                        "subject_id": "NCB204-B24071",
                        "packet_item": "CMO audit commitment 2025-14",
                        "source": "data/release_packets.csv",
                        "record_id": "NCB204-B24071:CMO audit commitment 2025-14",
                        "evidence_refs": ["NCB204-B24071:CMO audit commitment 2025-14"],
                    }
                ],
                "abstentions": [],
                "contradictions": [],
                "evidence": [],
                "human_review": {},
            },
            title="Batch",
        )
        self.assertIn("cmo_commitment_missing", html)
        self.assertIn("CMO audit commitment 2025-14", html)
        self.assertIn("data/release_packets.csv", html)
        self.assertIn("Viewed", html)
        self.assertIn('class="viewed-check"', html)
        self.assertIn('class="viewed-mark"', html)
        self.assertIn('type="checkbox"', html)
        self.assertIn('data-record="', html)
        self.assertIn('hx-trigger="click"', html)

    def test_contradiction_shows_both_pack_positions(self) -> None:
        html = render_pack_page(
            {
                "request_id": "REQ-x",
                "findings": [],
                "gaps": [],
                "abstentions": [],
                "contradictions": [
                    {
                        "topic": "genealogy",
                        "source": "data/material_genealogy.csv",
                        "record_id": "SUA-88",
                        "values": ["missing_branch", "issued"],
                        "left": {
                            "value": "missing_branch",
                            "source": "data/material_genealogy.csv",
                            "record_id": "NCB204-B24071:SUA-88",
                        },
                        "right": {
                            "value": "issued",
                            "source": "data/warehouse_movements.csv",
                            "record_id": "WM-90",
                        },
                        "evidence_refs": ["NCB204-B24071:SUA-88", "WM-90"],
                    }
                ],
                "evidence": [],
                "human_review": {},
            },
            title="Batch",
        )
        self.assertIn("missing_branch", html)
        self.assertIn("issued", html)
        self.assertIn("Position A", html)
        self.assertIn("Position B", html)
        self.assertNotIn("resolve", html.casefold())
        self.assertIn('data-record="NCB204-B24071:SUA-88"', html)
        self.assertIn('data-record="WM-90"', html)
        self.assertNotIn('data-record="NCB204-B24071:SUA-88" checked', html)
        self.assertNotIn('data-record="WM-90" checked', html)

    def test_graph_projection_is_shown_when_present(self) -> None:
        html = render_pack_page(
            {
                "request_id": "REQ-x",
                "findings": [],
                "gaps": [],
                "abstentions": [],
                "contradictions": [],
                "evidence": [],
                "human_review": {
                    "graph_projection": {
                        "store": "in_process",
                        "source": "data/RELATIONSHIP_MODEL.csv",
                        "node_count": 2,
                        "edge_count": 1,
                        "seed": "batches.csv:NCB204-B24071",
                        "visited": ["batches.csv:NCB204-B24071", "lab_results.csv:LR-88"],
                        "frontier": [],
                        "traversal_incomplete": False,
                        "hops_used": 1,
                        "max_hops": 4,
                    }
                },
            },
            title="Batch",
        )
        self.assertIn("Knowledge graph · per-run projection", html)
        self.assertIn("Not a system of record", html)
        self.assertIn("batches.csv:NCB204-B24071", html)
        self.assertIn("lab_results.csv:LR-88", html)

    def test_abstention_shows_units(self) -> None:
        html = render_pack_page(
            {
                "request_id": "REQ-x",
                "findings": [],
                "gaps": [],
                "abstentions": [
                    {
                        "reason_code": "unit_mapping_unapproved",
                        "subject_id": "LR-88",
                        "observed_unit": "mg/L",
                        "spec_unit": "ug/mL",
                        "evidence_refs": ["LR-88"],
                    }
                ],
                "contradictions": [],
                "evidence": [],
                "human_review": {},
            },
            title="Batch",
        )
        self.assertIn("unit_mapping_unapproved", html)
        self.assertIn("mg/L", html)
        self.assertIn("ug/mL", html)

    def test_rules_only_banner_when_no_model_text(self) -> None:
        html = render_pack_page(
            {
                "request_id": "REQ-x",
                "findings": [],
                "gaps": [],
                "abstentions": [],
                "contradictions": [],
                "evidence": [],
                "human_review": {},
            },
            title="Batch",
        )
        self.assertIn("Rules-only pack", html)
