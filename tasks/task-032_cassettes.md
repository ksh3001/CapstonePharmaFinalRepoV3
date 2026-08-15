# TASK-032 — Cassette replay and L6a groundedness

**Goal:** record-and-replay keyed by prompt, deployment and model version. Evals make zero live calls. Groundedness is the G-1…G-5 guard, not a judge.

## Specs to load

FR-013 BR-110; plan §25.8; NFR-21, NFR-22, NFR-24; AC-FR013-13, AC-FR013-18.

Do not call Azure from evals.

## Out of scope

Live recording against a paid endpoint.

## Steps

1. `packages/advice/cassettes.py` hashes the cassette key.
2. `evals/graders/deterministic/groundedness.py` reuses `guard_advice`.

## Done when

`python -m aegis test` is green; `tests/regression/test_advice_replay.py` and `tests/eval/test_groundedness.py` pass.
