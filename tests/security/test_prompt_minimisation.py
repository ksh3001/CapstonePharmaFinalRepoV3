from __future__ import annotations

import json
import os
import unittest

from packages.advice.minimise import minimise_pack
from packages.kernel.checkpoint import reset_replay
from packages.kernel.packs import advisory_pack
from services.integration.azure.openai import AzureOpenAIAdapter
from tests.helpers import load_pub


class PromptMinimisationTests(unittest.TestCase):
    def test_direct_identifiers_are_redacted_before_prompt(self) -> None:
        reset_replay()
        pack = advisory_pack(load_pub("PUB-13"))
        pack["patient_id"] = "P-SECRET"
        minimised = minimise_pack(pack)
        rendered = json.dumps(minimised)
        self.assertNotIn("P-SECRET", rendered)
        self.assertIn("PN-redacted", rendered)
        old = os.environ.get("AEGIS_RUNTIME_MODE")
        os.environ["AEGIS_RUNTIME_MODE"] = "assessment"
        try:
            result = AzureOpenAIAdapter().generate(pack)
            self.assertEqual(result["outbound"], 0)
        finally:
            if old is None:
                os.environ.pop("AEGIS_RUNTIME_MODE", None)
            else:
                os.environ["AEGIS_RUNTIME_MODE"] = old
