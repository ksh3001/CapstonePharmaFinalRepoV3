from __future__ import annotations

import unittest

from packages.config.paths import repo_root
from compliance.tripwires.evaluate import CLAIM, evaluate


class TripwireTests(unittest.TestCase):
    def test_control_map_rows_have_test_and_evidence(self) -> None:
        result = evaluate()
        self.assertTrue(result["ok"], result.get("failed") or result.get("unmapped"))
        self.assertGreaterEqual(int(result["controls"]), 15)
        self.assertEqual(result["claim"], CLAIM)
        abuse = (repo_root() / "compliance" / "eu-ai-act" / "abuse_monitoring.md").read_text(encoding="utf-8")
        self.assertIn("no Limited Access exemption", abuse)
        self.assertIn("pseudonymis", abuse.casefold())

    def test_artefact19_tripwires_all_pass(self) -> None:
        result = evaluate()
        failed = result.get("failed") or []
        self.assertEqual(failed, [], failed)
        ids = {str(item["id"]) for item in result["tripwires"]}
        self.assertTrue(
            {
                "write-tools",
                "human-review",
                "model-pin",
                "residency",
                "deny-list",
                "thresholds",
                "change-classes",
            }.issubset(ids)
        )

    def test_governance_docs_state_the_posture(self) -> None:
        root = repo_root()
        intended = (root / "docs" / "product" / "intended-use.md").read_text(encoding="utf-8").casefold()
        self.assertIn("advisory", intended)
        self.assertIn("does not", intended)
        self.assertIn("human", intended)
        aims = (root / "docs" / "governance" / "aims-scope.md").read_text(encoding="utf-8").casefold()
        self.assertIn("interested parties", aims)
        self.assertIn("scope", aims)
        policy = (root / "docs" / "governance" / "ai-policy.md").read_text(encoding="utf-8")
        self.assertIn("Decide", policy)
        self.assertIn("deterministic", policy.casefold())
        mapping = (root / "compliance" / "iso42001" / "mapping.md").read_text(encoding="utf-8").casefold()
        self.assertIn("clause", mapping)
        incident = (root / "ops" / "runbooks" / "incident.md").read_text(encoding="utf-8").casefold()
        self.assertIn("kill switch", incident)
        self.assertIn(CLAIM.casefold(), incident)
