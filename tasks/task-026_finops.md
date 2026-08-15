# TASK-026 — FinOps: cost per successful task and wallet ceilings

**Goal:** reproduce inference cost from tokens and listed prices; denominator is successful tasks; missing review cost is a gap; wallet exhaustion refuses new runs.

## Specs to load

`specs/features/FR-007`; AC-FR007-01…12, AC-FR007-10a.

Do not serialise binary floats. Do not present an estimated or assumed cost. Do not put `"truncated answer"` in a budget-stop statement.

## Out of scope

Live Azure billing APIs · changing engines.

## Steps

1. `packages/domain/finops.py` constructs gaps and abstentions (MR-5).
2. `packages/finops/wallet.py` admits runs under a cumulative ceiling.
3. `python -m aegis run --workflow finops` emits PUB-14.

## Done when

`python -m aegis test` is green; FinOps unit/security/performance tests pass.
