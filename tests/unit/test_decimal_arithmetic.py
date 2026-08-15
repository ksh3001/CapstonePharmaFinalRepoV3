from __future__ import annotations

import unittest
from decimal import Decimal

from packages.domain.finops import ROUNDING, _dec
from packages.kernel.canonical import dumps, FloatRejected


class DecimalArithmeticTests(unittest.TestCase):
    def test_no_binary_float_in_pack_and_rounding_is_declared(self) -> None:
        self.assertEqual(str(ROUNDING), "ROUND_HALF_EVEN")
        value = _dec("8.50") * Decimal("5.8")
        self.assertIsInstance(value, Decimal)
        with self.assertRaises(FloatRejected):
            dumps({"amount": 1.25})
