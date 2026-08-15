# TASK-020 — OrchestratorPort, declared graph, stdlib runner, budgets

**Goal:** sequence every workflow through a static step graph and declared budgets. The stdlib runner is the assessed path. Domain engines remain the source of truth.

## Specs to load

`specs/features/FR-006` · `specs/data/state_transitions.md` §3 · plan §20 · NFR-07.

Do not add LangGraph (TASK-021). Do not call Azure OpenAI (TASK-030). Do not implement cost-per-successful-task (TASK-026).

## Out of scope

Dynamic replanning · model-chosen next step · LangGraph checkpointer · wallet ceilings · PHI in checkpoint state.

## Steps

1. `OrchestratorPort.run(request) -> pack` with a stdlib implementation in `packages/orchestrator/deterministic.py`.
2. Declared steps are fixed: admit, plan, retrieve, project_graph, reconcile, annotate, approve, package, validate_emit.
3. Budgets live in `packages/config/budgets.py` (`MAX_TOKENS_PER_REQUEST = 50000`). Undeclared ceilings refuse to start.
4. A checkpoint of references, hashes and counters is persisted before each step (`durability: sync`).
5. Exhaustion emits a schema-valid partial pack with `budget_stop`. Retry exhaustion terminates; a loop is not a strategy.
6. A proposed step outside the graph is refused and recorded; the pack matches the clean run.
7. `DR-1` / `DR-2` remain `status: draft` with `no_side_effects: true`.

## Done when

`python -m aegis test` is green; `python -m aegis run --workflow agent` emits a schema-valid PUB-13 pack through the stdlib runner.
