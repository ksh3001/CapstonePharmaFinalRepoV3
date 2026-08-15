# TASK-016 — Checkpoint freshness and idempotent replay

**Goal:** stale or hash-mismatched checkpoints never auto-resume; the same idempotency key returns the original pack and creates no new drafts.

## Specs to load

FR-003 BR-030 / AC-FR003-09, 10, 14 · FR-006 BR-052/053 / AC-FR006-02, 03, 05 · FR-002 AC-FR002-16 · plan §20.4.

Do not implement `OrchestratorPort` (TASK-020). Do not persist PHI in checkpoints.

## Out of scope

LangGraph checkpointer · budget stop · personal data in checkpoint payloads (AC-FR006-06 stays TASK-020).

## Steps

1. Freshness bound lives in `packages/config/checkpoint.py` (PUB-13's 380 minutes exceeds it).
2. Replay store returns the original pack bytes without re-running the engine.
3. AR-77 reports DR-1 and DR-2 as pre-existing drafts; no DR-3.
4. Serialisation commission with an empty pallet is an aggregation gap; no parent is inferred.
5. Complaint/batch/ICSR shared lot within ±30 days is `unconfirmed_link`; outside the window the candidate is absent.

## Done when

`python -m aegis test` is green; PUB-13 does not auto-resume; supply replay does not increment reconcile.
