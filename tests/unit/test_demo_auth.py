from __future__ import annotations

import unittest

from packages.config.demo_auth import demo_credential_hint, verify_demo_password


class DemoAuthTests(unittest.TestCase):
    def test_known_demo_password(self) -> None:
        self.assertTrue(verify_demo_password("qp_eu_1", "aegis-demo"))
        self.assertFalse(verify_demo_password("qp_eu_1", "wrong"))
        self.assertFalse(verify_demo_password("contractor_77", "aegis-demo"))

    def test_hint_lists_walkthrough_credentials(self) -> None:
        self.assertIn("qp_eu_1 / aegis-demo", demo_credential_hint())
