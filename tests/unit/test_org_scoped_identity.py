from __future__ import annotations

import unittest

from packages.ontology.identity import parse_identifier, resolve_identity


class OrgScopedIdentityTests(unittest.TestCase):
    def test_same_local_string_different_org_is_not_same(self) -> None:
        ntg = parse_identifier("NTG|NCB-204")
        biox = parse_identifier("BIOX|NCB-204")
        result = resolve_identity(ntg, biox, mappings=())
        self.assertNotEqual(result.verdict, "SAME")
        self.assertEqual(result.verdict, "IdentityConflict")
        self.assertEqual(result.reason_code, "cross_organisation_unmapped")
        self.assertEqual(ntg.value, biox.value)
        self.assertNotEqual(ntg.org_namespace, biox.org_namespace)

    def test_same_org_same_value_is_same(self) -> None:
        left = parse_identifier("CMO-IE|NCB204-B24071")
        right = parse_identifier("CMO-IE|NCB204-B24071")
        result = resolve_identity(left, right, mappings=())
        self.assertEqual(result.verdict, "SAME")
