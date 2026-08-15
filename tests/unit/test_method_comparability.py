from __future__ import annotations

import unittest

from packages.ontology.types import Quantity
from packages.ontology.units import compare_measurements


class MethodComparabilityTests(unittest.TestCase):
    def test_different_method_versions_are_not_trended(self) -> None:
        left = Quantity(value="0.92", unit_code="%", unit_system="UCUM")
        right = Quantity(value="0.91", unit_code="%", unit_system="UCUM")
        result = compare_measurements(
            left,
            right,
            left_method="potency_hplc",
            left_method_version="v3",
            right_method="potency_hplc",
            right_method_version="v4",
            comparability_approved=False,
        )
        self.assertFalse(result.comparable)
        self.assertEqual(result.reason_code, "method_comparability_unapproved")
        self.assertIsNone(result.converted_value)

    def test_approved_assessment_allows_unit_rule_only(self) -> None:
        left = Quantity(value="0.92", unit_code="%", unit_system="UCUM")
        right = Quantity(value="0.91", unit_code="%", unit_system="UCUM")
        result = compare_measurements(
            left,
            right,
            left_method="potency_hplc",
            left_method_version="v3",
            right_method="potency_hplc",
            right_method_version="v4",
            comparability_approved=True,
        )
        self.assertTrue(result.comparable)
        self.assertIsNone(result.converted_value)
