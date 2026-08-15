from __future__ import annotations

import unittest

from packages.ontology.types import Quantity
from packages.ontology.units import REASON_UNAPPROVED, compare_quantities
from packages.kernel.packs import batch_pack
from tests.helpers import load_pub, walk_converted


CRO_MAPPING = (
    {
        "interface": "CRO_LAB_TO_LIMS",
        "source_unit": "mg/L",
        "target_unit": "ug/mL",
        "conversion_rule": "1:1_assumed",
        "approved": "no",
    },
)


class UnitMappingTests(unittest.TestCase):
    def test_cq2_lr88_is_not_comparable_and_not_converted(self) -> None:
        observed = Quantity(value="0.92", unit_code="mg/L", unit_system="UCUM")
        spec = Quantity(value="0.85-1.05", unit_code="ug/mL", unit_system="UCUM")
        result = compare_quantities(observed, spec, mappings=CRO_MAPPING, as_of="2026-08-01T08:00:00Z")
        self.assertFalse(result.comparable)
        self.assertEqual(result.reason_code, REASON_UNAPPROVED)
        self.assertIsNone(result.converted_value)

    def test_identical_units_are_comparable_without_mapping(self) -> None:
        left = Quantity(value="98.7", unit_code="%", unit_system="UCUM")
        right = Quantity(value="98.0", unit_code="%", unit_system="UCUM")
        result = compare_quantities(left, right, mappings=CRO_MAPPING)
        self.assertTrue(result.comparable)
        self.assertIsNone(result.converted_value)

    def test_approved_mapping_still_emits_no_converted_number(self) -> None:
        approved = (
            {
                "interface": "M-1",
                "source_unit": "mg/L",
                "target_unit": "ug/mL",
                "conversion_rule": "1:1",
                "approved": "yes",
            },
        )
        left = Quantity(value="0.92", unit_code="mg/L", unit_system="UCUM")
        right = Quantity(value="0.92", unit_code="ug/mL", unit_system="UCUM")
        result = compare_quantities(left, right, mappings=approved)
        self.assertTrue(result.comparable)
        self.assertEqual(result.mapping_id, "M-1")
        self.assertIsNone(result.converted_value)

    def test_pub01_pack_records_unit_abstention_without_converted_number(self) -> None:
        pack = batch_pack(load_pub("PUB-01"), batch_id="NCB204-B24071")
        reasons = [item.get("reason_code") for item in pack["abstentions"]]
        self.assertIn(REASON_UNAPPROVED, reasons)
        subjects = [item.get("subject_id") for item in pack["abstentions"]]
        self.assertIn("LR-88", subjects)
        self.assertEqual(walk_converted(pack), [])
        lr88 = next(item for item in pack["evidence"] if item.get("record_id") == "LR-88")
        self.assertEqual(lr88["facts"]["value"], "0.92")
        self.assertEqual(lr88["facts"]["unit"], "mg/L")
        self.assertEqual(lr88["facts"]["spec"], "0.85-1.05 ug/mL")
