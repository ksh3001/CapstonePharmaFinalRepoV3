"""Runtime orchestrator resolution. packages/ stays stdlib-only."""

from __future__ import annotations

from packages.config.runtime import runtime_mode
from packages.orchestrator.deterministic import StdlibOrchestrator
from packages.orchestrator.port import OrchestratorPort
from services.integration.langgraph.adapter import LANGGRAPH_MODES, LangGraphOrchestrator


def resolve_runtime_orchestrator() -> OrchestratorPort:
    if runtime_mode() in LANGGRAPH_MODES:
        return LangGraphOrchestrator()
    return StdlibOrchestrator()
