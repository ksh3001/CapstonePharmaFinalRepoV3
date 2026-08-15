from __future__ import annotations

import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FORBIDDEN_DEFAULTS = (
    "AZURE_OPENAI_MODEL_VERSION=latest",
    "AZURE_OPENAI_MODEL_VERSION=current",
    "AZURE_OPENAI_MODEL_VERSION=alias",
    'os.environ.get("AZURE_OPENAI_MODEL_VERSION", "latest")',
    "gpt-4o-latest",
)


class ModelPinningTests(unittest.TestCase):
    def test_env_example_has_no_floating_alias_or_api_key_slot(self) -> None:
        text = (REPO / ".env.example").read_text(encoding="utf-8")
        self.assertNotIn("AZURE_OPENAI_API_KEY", text)
        for token in FORBIDDEN_DEFAULTS:
            self.assertNotIn(token, text)
        self.assertIn("AZURE_OPENAI_MODEL_VERSION=", text)

    def test_source_does_not_default_to_a_floating_alias(self) -> None:
        roots = [REPO / "packages", REPO / "services", REPO / "aegis"]
        hits: list[str] = []
        for root in roots:
            for path in root.rglob("*.py"):
                if "__pycache__" in path.parts:
                    continue
                text = path.read_text(encoding="utf-8")
                for token in FORBIDDEN_DEFAULTS:
                    if token in text:
                        hits.append(f"{path}: {token}")
        self.assertEqual(hits, [])
