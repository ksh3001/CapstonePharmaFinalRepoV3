from __future__ import annotations

import unittest

from packages.ontology.identity import parse_identifier, resolve_identity
from packages.ontology.types import Identifier


class IdentityTierTests(unittest.TestCase):
    def test_approved_mapping_is_same_by_mapping(self) -> None:
        left = Identifier(scheme="erp", value="NCB204-DE", org_namespace="NTG")
        right = Identifier(scheme="idmp", value="NCB-204", org_namespace="NTG")
        mappings = (
            {
                "local_product": "NCB204-DE",
                "idmp_product": "NCB-204",
                "mapping_status": "approved",
            },
        )
        result = resolve_identity(left, right, mappings=mappings)
        self.assertEqual(result.verdict, "SAME_BY_MAPPING")
        self.assertEqual(result.mapping_id, "NCB204-DE->NCB-204")

    def test_ambiguous_idmp_mapping_is_conflict(self) -> None:
        left = Identifier(scheme="erp", value="NCB204-DE", org_namespace="NTG")
        right = Identifier(scheme="idmp", value="NCB-204", org_namespace="NTG")
        mappings = (
            {
                "local_product": "NCB204-DE",
                "idmp_product": "NCB-204",
                "mapping_status": "ambiguous_strength_presentation",
            },
        )
        result = resolve_identity(left, right, mappings=mappings)
        self.assertEqual(result.verdict, "IdentityConflict")
        self.assertEqual(result.reason_code, "mapping_not_approved")

    def test_declared_edge_is_related_never_same(self) -> None:
        batch = parse_identifier("CMO-IE|NCB204-B24071")
        lot = parse_identifier("CMO-IE|MAT-01")
        result = resolve_identity(batch, lot, mappings=(), declared_edges=((batch, lot),))
        self.assertEqual(result.verdict, "RELATED")

    def test_draft_mapping_is_conflict(self) -> None:
        left = Identifier(scheme="erp", value="X", org_namespace="NTG")
        right = Identifier(scheme="idmp", value="Y", org_namespace="NTG")
        mappings = ({"local_product": "X", "idmp_product": "Y", "mapping_status": "draft"},)
        result = resolve_identity(left, right, mappings=mappings)
        self.assertEqual(result.verdict, "IdentityConflict")
