"""Resolve the assessed runner. Assessment is stdlib; LangGraph is selected in services/."""

from __future__ import annotations

from packages.orchestrator.deterministic import StdlibOrchestrator
from packages.orchestrator.port import OrchestratorPort


def resolve_orchestrator() -> OrchestratorPort:
    return StdlibOrchestrator()
