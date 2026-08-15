# TASK-033 — Evidence store: append-only chain and outcome record

**Goal:** one chain per request with request, inputs, pack hash, decisions, audit and exactly one `outcome` from the closed nine. Unwritable store fails closed. Tamper names the first broken link.

## Specs to load

`specs/features/FR-014`; plan §35; AC-FR014-01…06, 11–14, 16.

Do not store pack bodies or prompt bodies. Do not import kernel from `packages/evidence_store`. Classification types stay in domain (MR-5).

## Out of scope

Retention (TASK-034) · WORM (TASK-035) · Azure calls (TASK-030).

## Steps

1. `packages/evidence_store/` writes JSONL under `out/evidence/chains/`.
2. CLI: `python -m aegis evidence --request-id` and `verify-evidence`.
3. `persist_run` is invoked from pack builders after the pack is final.

## Done when

`python -m aegis test` is green; evidence chain, tamper, fail-closed, scan, retrieval, index and outcome tests pass.
