"""InferencePort. Azure adapter lives under services/; assessment never calls a network."""

from __future__ import annotations

from typing import Any, Protocol


class InferencePort(Protocol):
    def generate(self, pack: dict[str, Any]) -> dict[str, Any]: ...
