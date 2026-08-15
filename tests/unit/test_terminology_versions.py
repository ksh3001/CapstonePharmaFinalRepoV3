from __future__ import annotations

import unittest

from packages.ontology.terminology import equivalent, retain_coding, same_clinical_theme_not_equivalent


class TerminologyVersionTests(unittest.TestCase):
    def test_meddra_versions_are_not_equivalent(self) -> None:
        legacy = retain_coding("Anaphylactic reaction", "MedDRA", "27.1")
        current = retain_coding("Infusion related reaction", "MedDRA", "28.0")
        self.assertFalse(equivalent(legacy, current))
        self.assertTrue(same_clinical_theme_not_equivalent(legacy, current))

    def test_same_version_same_term_is_equivalent(self) -> None:
        left = retain_coding("Anaphylactic reaction", "MedDRA", "27.1")
        right = retain_coding("Anaphylactic reaction", "MedDRA", "27.1")
        self.assertTrue(equivalent(left, right))
        self.assertEqual(left.version, "27.1")
