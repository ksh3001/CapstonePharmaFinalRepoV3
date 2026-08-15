from __future__ import annotations

import unittest

from packages.advice.cassettes import cassette_key, load_cassette, save_cassette
from packages.kernel.canonical import dumps


class AdviceReplayTests(unittest.TestCase):
    def test_cassette_replay_is_byte_identical_with_zero_live_calls(self) -> None:
        payload = {
            "text": "Model-generated summary of the pack.",
            "labelled": "model-generated",
            "outbound": 0,
        }
        key = cassette_key("prompt-a", "dep", "2024-05-01")
        save_cassette(key, payload)
        first = load_cassette(key)
        second = load_cassette(key)
        self.assertEqual(dumps(first), dumps(second))
        self.assertEqual(first["outbound"], 0)
        other = cassette_key("prompt-b", "dep", "2024-05-01")
        self.assertNotEqual(key, other)
        self.assertIsNone(load_cassette(other))
