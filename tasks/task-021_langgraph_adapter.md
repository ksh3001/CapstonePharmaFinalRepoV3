# TASK-021 — LangGraph adapter with byte-parity against the stdlib runner

**Goal:** prove the optional LangGraph adapter emits the same pack bytes as the assessed stdlib runner, including after a model-name swap. Assessment does not install LangGraph.

## Specs to load

`specs/features/FR-006` BR-056 / AC-FR006-10 · plan §20.2.

Do not put domain logic in graph nodes. Do not call Azure OpenAI (TASK-030). Do not change `resolve_orchestrator()` off stdlib.

## Out of scope

LangGraph checkpointer · dynamic replanning · MCP · wallet ceilings.

## Steps

1. `services/integration/langgraph/adapter.py` implements `LangGraphOrchestrator` behind the same port.
2. Missing `langgraph` falls through to `StdlibOrchestrator` so assessment stays zero-install.
3. When present, a 1-node graph still delegates to the stdlib engine; recursion limit is `len(DECLARED_STEPS) + 2`.
4. `packages/` must not import `services/`.
5. Parity tests cover all 15 public fixtures and an `AEGIS_MODEL` swap.

## Done when

`python -m aegis test` is green; `tests/orchestration/test_parity.py` shows byte identity.
