from __future__ import annotations

import unittest

from packages.config.paths import repo_root


class NoAiBaselineTests(unittest.TestCase):
    def test_no_ai_baseline_is_compared_including_when_it_wins(self) -> None:
        text = (repo_root() / "docs" / "product" / "no-ai-baseline.md").read_text(encoding="utf-8")
        folded = text.casefold()
        self.assertIn("INJ-003", text)
        self.assertIn("no-ai", folded)
        self.assertIn("when the no-ai baseline wins", folded)
        self.assertIn("ai_disabled", folded)
        self.assertIn("byte-identical", folded)
        self.assertIn("generative ai", folded)
