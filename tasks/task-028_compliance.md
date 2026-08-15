# TASK-028 — Compliance tripwires

**Goal:** every control-map row names a test and an evidence path. AMB-13 records the safe default: no Limited Access exemption.

## Specs to load

plan §22, §23; `compliance/control-map.csv`.

Do not invent new BRs or ACs.

## Out of scope

Authoring further EU AI Act legal opinions.

## Steps

1. `compliance/tripwires/evaluate.py` fails closed on unmapped rows.
2. `compliance/eu-ai-act/abuse_monitoring.md` states the safe default.

## Done when

`python -m aegis test` is green; `tests/compliance/test_tripwires.py` passes.
