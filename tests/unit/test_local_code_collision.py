from __future__ import annotations

import unittest

from packages.ontology.identity import local_code_collision, parse_identifier, resolve_identity


class LocalCodeCollisionTests(unittest.TestCase):
    def test_collision_retains_both_and_selects_neither(self) -> None:
        first = parse_identifier("NTG|LOT-77")
        second = parse_identifier("BIOX|LOT-77")
        self.assertTrue(local_code_collision(first, second))
        result = resolve_identity(first, second, mappings=())
        self.assertEqual(result.verdict, "IdentityConflict")
        retained = {first.org_namespace, second.org_namespace}
        self.assertEqual(retained, {"NTG", "BIOX"})
        self.assertIsNone(result.mapping_id)
