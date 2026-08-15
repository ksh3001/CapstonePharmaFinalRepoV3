from __future__ import annotations

import unittest

from packages.config.paths import repo_root


class BenefitClaimsTests(unittest.TestCase):
    def test_business_case_rejects_reduced_review(self) -> None:
        text = (repo_root() / "docs" / "product" / "business-case.md").read_text(encoding="utf-8")
        folded = text.casefold()
        self.assertIn("quality authority", folded)
        self.assertIn("cycle-time", folded)
        self.assertIn("reduced review", folded)
        self.assertIn("rejected", folded)
        self.assertIn("INJ-001", text)
