from __future__ import annotations

import unittest

from packages.config.paths import repo_root


class MetricConflictTests(unittest.TestCase):
    def test_success_metrics_name_the_conflict_and_reject_a_single_objective(self) -> None:
        text = (repo_root() / "docs" / "product" / "success-metrics.md").read_text(encoding="utf-8")
        folded = text.casefold()
        self.assertIn("INJ-002", text)
        self.assertIn("throughput", folded)
        self.assertIn("deviation containment", folded)
        self.assertIn("service level", folded)
        self.assertIn("trade-off", folded)
        self.assertIn("no single metric", folded)
        self.assertIn("not a success measure", folded)
        self.assertIn("automation rate", folded)
