"""LangGraph adapter behind OrchestratorPort. Assessment does not require the library."""

from __future__ import annotations

from typing import Any, Callable

from packages.orchestrator.deterministic import StdlibOrchestrator
from packages.orchestrator.graph import DECLARED_STEPS, role_for_step

LANGGRAPH_MODES = frozenset({"advisory", "ui", "cloud"})


class LangGraphOrchestrator:
    """ui/cloud/advisory adapter. Nodes call the stdlib engine; they contain no domain logic."""

    def __init__(self, *, fail_hook: Callable[[str], None] | None = None) -> None:
        self._fail_hook = fail_hook
        self._app = None
        self._config: dict[str, Any] = {}
        self._engine: StdlibOrchestrator | None = None

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        compiled = _compile(self._fail_hook)
        if compiled is None:
            return StdlibOrchestrator(fail_hook=self._fail_hook).run(request)
        engine, invoke = compiled
        self._engine = engine
        state = engine.begin(request)
        if state.get("stopped"):
            return state["pack"]
        pause = bool(request.get("interrupt_on_approve"))
        result, app, config = invoke(state, engine, pause=pause)
        self._app = app
        self._config = config
        if result.get("__interrupt__"):
            return _awaiting_pack(engine, result)
        if result.get("stopped"):
            return result["pack"]
        return engine.finish(result)

    def resume(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._app is None or self._engine is None:
            raise RuntimeError("no interrupted LangGraph run to resume")
        from langgraph.types import Command

        result = self._app.invoke(Command(resume=payload), self._config)
        if result.get("__interrupt__"):
            return _awaiting_pack(self._engine, result)
        if result.get("stopped"):
            return result["pack"]
        return self._engine.finish(result)

    def declared_steps(self) -> tuple[str, ...]:
        return DECLARED_STEPS


def _compile(fail_hook: Callable[[str], None] | None):
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError:
        return None

    engine = StdlibOrchestrator(fail_hook=fail_hook, runner="langgraph")
    graph = StateGraph(dict)

    def _make_node(step_name: str):
        def node(state: dict[str, Any]) -> dict[str, Any]:
            if step_name == "approve" and engine._request.get("interrupt_on_approve"):
                from langgraph.types import interrupt

                interrupt(
                    {
                        "step": "approve",
                        "agent": role_for_step("approve", engine._workflow),
                        "request_id": str(engine._started.get("request_id") or ""),
                        "record_ids": list(engine._record_ids),
                    }
                )
            return engine.advance(state, step_name)

        return node

    for step in DECLARED_STEPS:
        graph.add_node(step, _make_node(step))
    graph.add_edge(START, DECLARED_STEPS[0])
    for index, step in enumerate(DECLARED_STEPS[:-1]):
        nxt = DECLARED_STEPS[index + 1]
        graph.add_conditional_edges(
            step,
            lambda state, nxt=nxt: END if state.get("stopped") else nxt,
            {nxt: nxt, END: END},
        )
    graph.add_edge(DECLARED_STEPS[-1], END)

    def invoke(
        state: dict[str, Any],
        bound: StdlibOrchestrator,
        *,
        pause: bool,
    ) -> tuple[dict[str, Any], Any, dict[str, Any]]:
        checkpointer = None
        config: dict[str, Any] = {"recursion_limit": len(DECLARED_STEPS) + 2}
        if pause:
            from langgraph.checkpoint.memory import MemorySaver

            checkpointer = MemorySaver()
            config["configurable"] = {"thread_id": str(bound._started.get("request_id") or "thread")}
        app = graph.compile(checkpointer=checkpointer)
        result = app.invoke(state, config)
        return result, app, config

    return engine, invoke


def _awaiting_pack(engine: StdlibOrchestrator, result: dict[str, Any]) -> dict[str, Any]:
    interrupts = result.get("__interrupt__") or ()
    payload = {}
    if interrupts:
        first = interrupts[0]
        payload = dict(getattr(first, "value", None) or {})
    review = {
        "orchestration": {
            "runner": "langgraph",
            "steps": list(DECLARED_STEPS),
            "steps_completed": list((result.get("steps_done") or [])),
            "awaiting": "approve",
            "agent": "AG-1",
        },
        "interrupt": payload,
    }
    pack = {
        "request_id": str(engine._started.get("request_id") or ""),
        "scenario_id": engine._scenario_id,
        "workflow": engine._workflow or "agent",
        "as_of": str((engine._fixture.get("authorized_context") or {}).get("as_of") or ""),
        "authorization": {
            "user": str((engine._fixture.get("authorized_context") or {}).get("user") or ""),
            "purpose": str((engine._fixture.get("authorized_context") or {}).get("purpose") or ""),
            "checked_at": str((engine._fixture.get("authorized_context") or {}).get("as_of") or ""),
            "decision": "allow",
        },
        "evidence": [],
        "contradictions": [],
        "gaps": [],
        "abstentions": [],
        "findings": [],
        "required_reviews": ["approve"],
        "human_review": review,
        "execution_status": "not_executed",
        "gate_outcome": "awaiting_human",
        "no_side_effects": True,
        "audit": {"hash_scope": "source_artifact"},
    }
    return pack
