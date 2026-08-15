# ADR-002: Deterministic engines are the source of truth

- Status: Accepted
- Date: 2026-08-13

## Decision

`packages/domain` decides. Orchestrator nodes sequence calls; they do not classify. `Contradiction`, `Gap`, and `Abstention` may be constructed only in `packages/domain` (MR-5).

## Consequences

The module-boundary gate fails the build if classification types are constructed elsewhere. Agents cannot become the architecture (R-10).
