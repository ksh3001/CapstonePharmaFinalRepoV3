from __future__ import annotations

import unittest

from packages.config.identities import (
    default_console_user,
    fixture_identities,
    resolve_identity,
)
from packages.config.roles import canonical_role, role_label


class IdentityConfigTests(unittest.TestCase):
    def test_fixture_table_is_the_source(self) -> None:
        users = {item.user: item for item in fixture_identities()}
        self.assertIn("qp_eu_1", users)
        self.assertIn("contractor_77", users)
        qp = users["qp_eu_1"]
        self.assertTrue(qp.assumable)
        self.assertEqual(qp.role_id, "qualified_person")
        self.assertEqual(qp.display_role, "EU Qualified Person")
        contractor = users["contractor_77"]
        self.assertFalse(contractor.assumable)
        self.assertIsNone(canonical_role(contractor.role_spelling))

    def test_unknown_user_does_not_resolve(self) -> None:
        self.assertIsNone(resolve_identity("reviewer_9"))
        self.assertEqual(default_console_user(), "qp_eu_1")
        self.assertEqual(role_label("qualified_person"), "EU Qualified Person")
