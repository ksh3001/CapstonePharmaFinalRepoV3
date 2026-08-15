from __future__ import annotations

import unittest

from services.api.console import render_pack_page


class AnnotationLabellingTests(unittest.TestCase):
    def test_annotations_are_labelled_model_generated(self) -> None:
        html = render_pack_page(
            {
                "request_id": "REQ-x",
                "findings": [],
                "gaps": [],
                "abstentions": [],
                "contradictions": [],
                "evidence": [],
                "human_review": {"annotations": [{"text": "A reviewer summary", "labelled": "model-generated"}]},
            },
            title="Batch",
        )
        self.assertIn("data-origin=\"model-generated\"", html)
        self.assertIn("Model-generated:", html)
