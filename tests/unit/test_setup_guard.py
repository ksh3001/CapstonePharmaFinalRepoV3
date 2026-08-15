from __future__ import annotations

import unittest

from packages.kernel.interpreter import InterpreterError, guard, is_supported


class SetupGuardTests(unittest.TestCase):
    def test_python_310_is_rejected(self) -> None:
        self.assertFalse(is_supported((3, 10, 14), "CPython"))
        with self.assertRaises(InterpreterError) as ctx:
            guard((3, 10, 14), "CPython")
        self.assertIn("3.10", str(ctx.exception))
        self.assertIn("3.11", str(ctx.exception))

    def test_python_311_and_312_are_accepted(self) -> None:
        self.assertTrue(is_supported((3, 11, 9), "CPython"))
        self.assertTrue(is_supported((3, 12, 10), "CPython"))
        guard((3, 11, 0), "CPython")
        guard((3, 12, 0), "CPython")

    def test_python_314_is_rejected(self) -> None:
        self.assertFalse(is_supported((3, 14, 0), "CPython"))

    def test_non_cpython_is_rejected(self) -> None:
        self.assertFalse(is_supported((3, 12, 0), "PyPy"))
