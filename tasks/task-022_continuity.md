# TASK-022 — Continuity, outage tolerance, kill switch and manual runbooks

**Goal:** read PUB-10 endpoint and tolerance evidence deterministically, refuse unvalidated substitution, keep the kill switch independent of inference, and require outage reconciliation before AI resumption.

## Specs to load

`specs/features/FR-009` (whole file).

Do not copy `knowledge/AI_DISABLED_CONTINUITY.md` into pack strings. Do not treat empty tolerance as zero or unlimited. Do not substitute `fallback_small`.

## Out of scope

Failing over infrastructure · executing the manual runbook · Azure OpenAI (TASK-030).

## Steps

1. `packages/domain/continuity.py` constructs classification types (MR-5).
2. `pv_intake` at 0 hours is manual immediately; 14-day workflows continue degraded with the deadline stated.
3. Empty tolerance fields raise `tolerance_not_specified`.
4. Manual runbooks live under `docs/runbooks/` and a missing runbook is a gap.
5. Isolated sources are stale by declaration; incident-window writes are `integrity_unconfirmed`.
6. Manual outage assignments keep provenance; recovered system rows are retained beside them.

## Done when

`python -m aegis test` is green; `python -m aegis run --workflow reliability` emits a schema-valid PUB-10 pack.
