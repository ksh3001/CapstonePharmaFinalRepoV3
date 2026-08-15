from __future__ import annotations

import unittest

from services.integration.azure.blob import ImmutableBlobError, put_immutable, worm_root


class BlobImmutabilityTests(unittest.TestCase):
    def test_overwrite_of_worm_object_is_rejected(self) -> None:
        name = "chain-pub-01.json"
        target = worm_root() / name
        if target.exists():
            target.unlink()
        policy = worm_root() / f"{name}.policy"
        if policy.exists():
            policy.unlink()
        put_immutable(name, {"request_id": "REQ-WORM", "immutable": True})
        with self.assertRaises(ImmutableBlobError):
            put_immutable(name, {"request_id": "REQ-WORM", "immutable": False})
        self.assertTrue((worm_root() / f"{name}.policy").is_file())
