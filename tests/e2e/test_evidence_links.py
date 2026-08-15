from __future__ import annotations

import unittest

from services.api.console import render_pack_page


class EvidenceLinkTests(unittest.TestCase):
    def test_claim_links_show_provenance_fields(self) -> None:
        html = render_pack_page(
            {
                "request_id": "REQ-x",
                "findings": [],
                "gaps": [],
                "abstentions": [],
                "contradictions": [],
                "evidence": [
                    {
                        "source": "data/batches.csv",
                        "record_id": "NCB204-B24071",
                        "authority": "challenge-package",
                        "effective_at": None,
                        "retrieved_at": "2026-08-01T08:00:00Z",
                        "integrity": {"sha256": "a" * 64, "source_preserved": True},
                    }
                ],
                "human_review": {},
            },
            title="Batch",
        )
        self.assertIn("/evidence/NCB204-B24071", html)
        self.assertIn("data/batches.csv", html)
        self.assertIn("challenge-package", html)
        self.assertIn("2026-08-01T08:00:00Z", html)
        self.assertIn("a" * 64, html)
