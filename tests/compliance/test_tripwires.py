from __future__ import annotations

import unittest

from packages.config.paths import repo_root
from compliance.tripwires.evaluate import evaluate


class TripwireTests(unittest.TestCase):
    def test_control_map_rows_have_test_and_evidence(self) -> None:
        result = evaluate()
        self.assertTrue(result["ok"], result.get("unmapped"))
        self.assertGreaterEqual(int(result["controls"]), 1)
        abuse = (repo_root() / "compliance" / "eu-ai-act" / "abuse_monitoring.md").read_text(encoding="utf-8")
        self.assertIn("no Limited Access exemption", abuse)
        self.assertIn("pseudonymis", abuse.casefold())
