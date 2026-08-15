# TASK-027 — Eval harness L0–L6

**Goal:** deterministic graders for contract, deny-list, trajectory, subgroup-spread and byte identity. Judge scoring is not a release gate.

## Specs to load

plan §25.1–25.7; `evals/thresholds.yaml`; NFR-27.

Do not import `packages/` from evals into a way that breaks stdlib assessment. Do not enable judge gating.

## Out of scope

L6a cassettes (TASK-032) · Azure live calls.

## Steps

1. `evals/graders/deterministic/` implements L0–L6.
2. `evals/run_evals.py` grades PUB-01.
3. Subgroup spread cap is 0.15.

## Done when

`python -m aegis test` is green; `tests/eval/test_graders.py` passes.
