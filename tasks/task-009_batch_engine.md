# TASK-009 — Batch engine: contradictions, gaps, abstentions, readiness

**Goal:** produce a schema-valid batch pack for PUB-01 from deterministic rules.

## Specs to load

`specs/features/FR-001_batch_evidence_reconciliation.md` · `specs/api/api_contracts.md` · `packages/contracts/regulated/batch_response.schema.json`.

## Done when

PUB-01 validates against `batch_response.schema.json`; three consecutive dumps match; `python -m aegis test` is green.
