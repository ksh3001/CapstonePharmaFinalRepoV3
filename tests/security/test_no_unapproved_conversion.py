from __future__ import annotations

import unittest

from packages.kernel.packs import advisory_pack
from tests.helpers import load_pub, walk_converted


class NoUnapprovedConversionTests(unittest.TestCase):
    def test_pub12_emits_no_converted_number_from_unapproved_rule(self) -> None:
        pack = advisory_pack(load_pub("PUB-12"))
        self.assertEqual(walk_converted(pack), [])
        rendered = str(pack)
        self.assertNotIn("converted_value", rendered.replace("converted_value\": null", ""))
        self.assertNotIn("1:1_assumed result", rendered.casefold())
        reasons = [item.get("reason_code") for item in pack["abstentions"]]
        self.assertIn("unit_mapping_unapproved", reasons)
