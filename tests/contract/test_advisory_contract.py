from __future__ import annotations

import json
import unittest
from pathlib import Path

from packages.config.paths import synthetic_dir
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.kernel.packs import advisory_pack
from scripts.build_fixture_copyset import build


ADVISORY_FIXTURES = ("PUB-09", "PUB-10", "PUB-11", "PUB-12", "PUB-13", "PUB-14", "PUB-15")


def _ensure_copyset() -> Path:
    folder = synthetic_dir() / "evaluation" / "public_fixtures"
    if not folder.is_dir():
        build()
    return folder


class AdvisoryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixtures = _ensure_copyset()

    def test_seven_advisory_fixtures_resolve_and_validate(self) -> None:
        schema = resolve_contract("advisory_nonexecuting")
        for name in ADVISORY_FIXTURES:
            path = self.fixtures / f"{name}.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload.get("response_contract"), "advisory_nonexecuting", name)
            pack = advisory_pack(payload)
            validate(pack, schema)

    def test_all_fifteen_fixtures_resolve(self) -> None:
        for path in sorted(self.fixtures.glob("PUB-*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            resolve_contract(str(payload["response_contract"]))

    def test_unknown_contract_is_an_error(self) -> None:
        from packages.contracts.validator import SchemaError

        with self.assertRaises(SchemaError):
            resolve_contract("does_not_exist")
