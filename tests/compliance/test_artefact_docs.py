from __future__ import annotations

import unittest

from packages.config.paths import repo_root

ARTEFACTS = (
    ("docs/product/business-case.md", "INJ-001", "obligation"),
    ("docs/product/success-metrics.md", "INJ-002", "obligation"),
    ("docs/product/no-ai-baseline.md", "INJ-003", "obligation"),
    ("docs/product/patent-cliff.md", "INJ-004", "obligation"),
    ("docs/product/vendor-concentration.md", "INJ-078", "obligation"),
    ("docs/operations/vendor-exit.md", "INJ-083", "obligation"),
    ("docs/operations/retirement.md", "INJ-084", "obligation"),
    ("docs/runbooks/batch_review.md", "INJ-082", "obligation"),
    ("docs/runbooks/pv_intake.md", "INJ-082", "obligation"),
    ("docs/runbooks/supply_planning.md", "INJ-082", "obligation"),
)

INDEXED = (
    "docs/README.md",
    "docs/architecture/overview.md",
    "docs/engineering/developer-guide.md",
    "docs/quality/release-bar.md",
    "docs/security/posture.md",
    "docs/operations/operator-guide.md",
    "docs/product/intended-use.md",
    "docs/governance/aims-scope.md",
    "docs/governance/ai-policy.md",
)

FORBIDDEN = ("todo", "fixme", "placeholder", "lorem ipsum", "tbd")


class ArtefactDocsTests(unittest.TestCase):
    def test_inject_artefacts_have_required_sections(self) -> None:
        root = repo_root()
        for rel, inject, obligation in ARTEFACTS:
            text = (root / rel).read_text(encoding="utf-8")
            folded = text.casefold()
            with self.subTest(rel):
                self.assertTrue((root / rel).is_file(), rel)
                self.assertIn(inject, text)
                self.assertIn(obligation, folded)
                self.assertGreater(len(text.strip()), 200)
                for token in FORBIDDEN:
                    self.assertNotIn(token, folded)

    def test_fde_layers_answer_one_question(self) -> None:
        root = repo_root()
        register = (root / "docs" / "README.md").read_text(encoding="utf-8")
        for rel in INDEXED:
            text = (root / rel).read_text(encoding="utf-8")
            with self.subTest(rel):
                self.assertTrue((root / rel).is_file(), rel)
                self.assertTrue(
                    "question this file answers" in text.casefold() or rel == "docs/README.md",
                    rel,
                )
                name = rel.rsplit("/", 1)[-1]
                self.assertTrue(name in register or rel in register, rel)
                self.assertNotIn("lorem ipsum", text.casefold())
                self.assertNotIn("tbd", text.casefold())
