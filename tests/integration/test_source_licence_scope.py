from __future__ import annotations

import json
import unittest

from packages.domain.graph_findings import licence_scoped_claims


class SourceLicenceScopeTests(unittest.TestCase):
    def test_conflicting_claims_retained_and_barred_licence_excluded(self) -> None:
        claims = [
            {
                "dataset": "OPEN-1",
                "claim": "assay-A",
                "method": "HPLC-1",
                "date": "2026-06-01",
                "value": "98.1",
            },
            {
                "dataset": "OPEN-1",
                "claim": "assay-A",
                "method": "HPLC-2",
                "date": "2026-06-08",
                "value": "97.4",
            },
            {
                "dataset": "LIC-OMX-4",
                "claim": "secret-hcp-segment",
                "method": "panel",
                "date": "2026-05-01",
                "value": "must-not-appear",
            },
        ]
        licences = [
            {"dataset": "OPEN-1", "permitted_use": "HCP segmentation", "commercial_use": "no", "model_training": "no"},
            {"dataset": "LIC-OMX-4", "permitted_use": "research only", "commercial_use": "no", "model_training": "restricted"},
        ]
        view = licence_scoped_claims(claims, licences, purpose="HCP segmentation")
        self.assertTrue(any(item.get("gap_type") == "licence_scope" for item in view["gaps"]))
        self.assertTrue(any(item.get("subject_id") == "LIC-OMX-4" for item in view["gaps"]))
        methods = {item["method"] for item in view["claims"]}
        dates = {item["date"] for item in view["claims"]}
        self.assertEqual(methods, {"HPLC-1", "HPLC-2"})
        self.assertEqual(dates, {"2026-06-01", "2026-06-08"})
        rendered = json.dumps(view)
        self.assertNotIn("must-not-appear", rendered)
        self.assertNotIn("secret-hcp-segment", rendered)
        self.assertIn("HPLC-1", rendered)
        self.assertIn("HPLC-2", rendered)
