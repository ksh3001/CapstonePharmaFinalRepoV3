# TASK-029 — Inject fan-out and evidence export

**Goal:** `python -m aegis evidence-export` lists injects, CLI commands and a rebuilt store index.

## Specs to load

plan §3.3, §15.

Do not invent inject IDs. Do not weaken the inject-coverage gate.

## Out of scope

New BRs/ACs.

## Steps

1. Export includes inject id/title pairs from `data/injects.json`.
2. Commands include `evidence` and `verify-evidence`.

## Done when

`python -m aegis test` is green; `tests/integration/test_inject_export.py` passes.
