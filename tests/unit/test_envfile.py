from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from packages.config.envfile import load_envfile


class EnvfileTests(unittest.TestCase):
    def test_loads_names_and_maps_generator_deployment(self) -> None:
        old = {key: os.environ.get(key) for key in (
            "GENERATOR_DEPLOYMENT",
            "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_OPENAI_MODEL_VERSION",
            "AEGIS_RUNTIME_MODE",
        )}
        try:
            for key in old:
                os.environ.pop(key, None)
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / ".env"
                path.write_text(
                    "AEGIS_RUNTIME_MODE=advisory\nGENERATOR_DEPLOYMENT=gpt-4.1\n",
                    encoding="utf-8",
                )
                load_envfile(path, override=True)
            self.assertEqual(os.environ["AEGIS_RUNTIME_MODE"], "advisory")
            self.assertEqual(os.environ["AZURE_OPENAI_DEPLOYMENT"], "gpt-4.1")
            self.assertEqual(os.environ["AZURE_OPENAI_MODEL_VERSION"], "gpt-4.1")
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_does_not_override_existing_unless_asked(self) -> None:
        old = os.environ.get("AEGIS_RUNTIME_MODE")
        try:
            os.environ["AEGIS_RUNTIME_MODE"] = "assessment"
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / ".env"
                path.write_text("AEGIS_RUNTIME_MODE=advisory\n", encoding="utf-8")
                load_envfile(path, override=False)
            self.assertEqual(os.environ["AEGIS_RUNTIME_MODE"], "assessment")
        finally:
            if old is None:
                os.environ.pop("AEGIS_RUNTIME_MODE", None)
            else:
                os.environ["AEGIS_RUNTIME_MODE"] = old
