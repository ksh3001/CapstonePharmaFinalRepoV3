# Repository map

Authoritative tree: master build plan §2. This file orients a newcomer; the generated `STRUCTURE_MANIFEST.json` is the gate.

| Path | Role |
|---|---|
| `aegis/` | Stdlib CLI façade (`python -m aegis`). Imports `packages/*` only. |
| `packages/` | Stdlib core. Import gate + module-boundary gate apply here. |
| `packages/kernel/` | Request lifecycle, authZ, audit writer, canonical JSON. |
| `packages/domain/` | Engines and classification (`Contradiction` / `Gap` / `Abstention`). |
| `packages/contracts/` | Challenge schemas (hash-verified) + team advisory contract + deny-list. |
| `services/integration/` | Every third-party adapter. Nothing under `packages/` may import these. |
| `apps/web/` | Jinja templates + vendored HTMX/CSS for the HITL console. |
| `services/api/` | Stdlib JSON handlers + HTTP server; optional FastAPI in `fastapi_app.py`. |
| `specs/` | Authoritative build inputs, copied from the challenge `01_specs/`. |
| `tasks/` | Sitting-sized tasks with explicit spec lists. |
| `plans/active/` | Master build plan (index and rationale, not a build input). |
| `tests/` | Stdlib `unittest` suite. `python -m aegis test` discovers these. |
| `quality/static-analysis/` | Phase 0 gates: stdlib, inject coverage, module boundaries, nondeterminism. |
| `tests/fixtures/synthetic/` | Hash-verified copy set. Provenance in `PROVENANCE.csv`. |
| `evals/` | Datasets and graders (later phases). |
| `compliance/` | Control map and tripwires. |
| `docs/adr/` | Architecture decision records ADR-001…011. |
