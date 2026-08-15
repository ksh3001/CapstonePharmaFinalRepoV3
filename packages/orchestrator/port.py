"""OrchestratorPort: run(request) -> pack. No domain logic lives here."""

from __future__ import annotations

from typing import Any, Protocol


class OrchestratorPort(Protocol):
    def run(self, request: dict[str, Any]) -> dict[str, Any]: ...
