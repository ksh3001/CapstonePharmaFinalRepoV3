"""CPython interpreter pin: ≥ 3.11 and < 3.14 (AMB-08)."""

from __future__ import annotations

import platform
import sys


MIN_VERSION = (3, 11)
MAX_EXCLUSIVE = (3, 14)


class InterpreterError(SystemExit):
    """Raised (as SystemExit) when the interpreter is outside the supported range."""


def current_implementation() -> str:
    return platform.python_implementation()


def is_supported(
    version_info: tuple[int, ...] | None = None,
    implementation: str | None = None,
) -> bool:
    version = version_info if version_info is not None else sys.version_info
    impl = implementation if implementation is not None else current_implementation()
    if impl != "CPython":
        return False
    major_minor = (int(version[0]), int(version[1]))
    return MIN_VERSION <= major_minor < MAX_EXCLUSIVE


def guard(
    version_info: tuple[int, ...] | None = None,
    implementation: str | None = None,
) -> None:
    version = version_info if version_info is not None else sys.version_info
    impl = implementation if implementation is not None else current_implementation()
    detected = f"{impl} {version[0]}.{version[1]}.{version[2] if len(version) > 2 else 0}"
    if is_supported(version, impl):
        return
    message = (
        f"AEGIS requires CPython >= 3.11 and < 3.14; detected {detected}. "
        "Determinism claims are made for this range only."
    )
    raise InterpreterError(message)
