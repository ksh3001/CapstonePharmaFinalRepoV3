# TASK-034 — Retention and live hold engine

**Goal:** LLM/prompt logs expire at 90 days as a chain event. Active legal holds block expiry and record `hold_refusal`. Clinical and ICSR records never expire. Hold state is read live and never cached.

## Specs to load

FR-014 BR-119/121/122; AC-FR014-07…10.

Do not use `datetime.now`. Do not cache hold rows.

## Out of scope

WORM adapter (TASK-035).

## Steps

1. `packages/evidence_store/retention.py` compares `as_of` to `recorded_at`.
2. Holds are loaded from `legal_holds.csv` in the current fixture on every call.

## Done when

`python -m aegis test` is green; retention and hold tests pass.
