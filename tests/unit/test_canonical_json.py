from __future__ import annotations

import os
import unittest
from decimal import Decimal

from packages.kernel.canonical import (
    FloatRejected,
    derive_request_id,
    dumps,
    preserve_source_time,
    sort_evidence,
)


class CanonicalJsonTests(unittest.TestCase):
    def test_key_order_and_trailing_newline(self) -> None:
        payload = {"b": 1, "a": 2}
        encoded = dumps(payload)
        self.assertEqual(encoded, b'{"a":2,"b":1}\n')

    def test_utf8_and_lf(self) -> None:
        encoded = dumps({"note": "µ"})
        self.assertEqual(encoded, b'{"note":"\xc2\xb5"}\n')
        self.assertNotIn(b"\r", encoded)

    def test_reordering_records_does_not_change_bytes(self) -> None:
        first = [{"source": "b.csv", "record_id": "2"}, {"source": "a.csv", "record_id": "1"}]
        second = list(reversed(first))
        self.assertEqual(dumps({"evidence": sort_evidence(first)}), dumps({"evidence": sort_evidence(second)}))

    def test_float_is_rejected(self) -> None:
        with self.assertRaises(FloatRejected):
            dumps({"ratio": 0.1})

    def test_decimal_is_accepted(self) -> None:
        encoded = dumps({"ratio": Decimal("0.10")})
        self.assertEqual(encoded, b'{"ratio":"0.10"}\n')

    def test_source_time_is_verbatim(self) -> None:
        raw = "2026-07-10"
        self.assertEqual(preserve_source_time(raw), raw)
        self.assertEqual(preserve_source_time("2026-07-10T08:00:00"), "2026-07-10T08:00:00")

    def test_request_id_is_stable_and_sensitive(self) -> None:
        first = derive_request_id("PUB-01", "2026-08-01T08:00:00Z", "abc", "phase-0")
        second = derive_request_id("PUB-01", "2026-08-01T08:00:00Z", "abc", "phase-0")
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("REQ-"))
        self.assertEqual(len(first), 20)
        self.assertNotEqual(first, derive_request_id("PUB-02", "2026-08-01T08:00:00Z", "abc", "phase-0"))

    def test_hostile_environment_does_not_change_bytes(self) -> None:
        payload = {"z": "1", "a": "2"}
        original = dumps(payload)
        old_tz = os.environ.get("TZ")
        old_lang = os.environ.get("LANG")
        old_hash = os.environ.get("PYTHONHASHSEED")
        try:
            os.environ["TZ"] = "America/New_York"
            os.environ["LANG"] = "ja_JP.UTF-8"
            os.environ["PYTHONHASHSEED"] = "random"
            self.assertEqual(dumps(payload), original)
        finally:
            for key, value in (("TZ", old_tz), ("LANG", old_lang), ("PYTHONHASHSEED", old_hash)):
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
