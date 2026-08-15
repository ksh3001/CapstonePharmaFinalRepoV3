from __future__ import annotations

import unittest

from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from tests.helpers import fixture_with

SUPERSEDING = {
    "doc_id": "K-006",
    "file": "BATCH_RELEASE_EVIDENCE_POLICY.md",
    "authority": "NovaCura Global Policy",
    "effective": "2026-06-01",
    "status": "approved",
    "supersedes": "BATCH_RELEASE_POLICY_OLD.md",
}
SUPERSEDED = {
    "doc_id": "K-007",
    "file": "BATCH_RELEASE_POLICY_OLD.md",
    "authority": "Historical controlled document",
    "effective": "2024-01-01",
    "status": "superseded",
}


class SupersessionTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_replay()

    def test_superseded_and_superseding_both_appear_with_relationship(self) -> None:
        fixture = fixture_with(
            [
                {"source": "data/knowledge_catalog.csv", "records": [SUPERSEDING]},
                {"source": "data/knowledge_catalog.csv", "records": [SUPERSEDED]},
            ],
            scenario_id="SYN-SUPERSEDE",
            workflow="security",
        )
        pack = advisory_pack(fixture)
        validate(pack, resolve_contract("advisory_nonexecuting"))
        ids = {item["record_id"] for item in pack["evidence"]}
        self.assertIn("K-006", ids)
        self.assertIn("K-007", ids)
        links = pack["human_review"]["authority"]["supersessions"]
        self.assertTrue(links)
        self.assertEqual(links[0]["superseding"], "BATCH_RELEASE_EVIDENCE_POLICY.md")
        self.assertEqual(links[0]["superseded"], "BATCH_RELEASE_POLICY_OLD.md")
        self.assertTrue(links[0]["both_retained"])
