# ADR-008: LangGraph behind OrchestratorPort

- Status: Accepted
- Date: 2026-08-13

## Decision

`packages/orchestrator` defines `OrchestratorPort` and a deterministic stdlib runner used in `assessment` and `ai_disabled`. LangGraph implements the same port in `services/integration/langgraph/` for `ui` / `cloud` / `advisory`. Byte-parity against the stdlib runner is a safety property, not a convenience.

## Consequences

Domain logic must not live in graph nodes. LangGraph is an adapter. Checkpointer: Sqlite locally (file, offline); Redis only in `cloud`; references only, no PHI.
