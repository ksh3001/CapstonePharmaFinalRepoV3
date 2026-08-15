# TASK-014 — Supply engine

**Goal:** emit schema-valid `supply_options` packs with draft options, constraints, quality holds and approvals. No reserve, allocate, ship, release, recall or dispose action.

## Specs to load

`specs/features/FR-003` (whole file) · TASK-015 bounded graph already Done.

Do not implement checkpoint replay (TASK-016). Do not implement orchestration (TASK-020).

## Out of scope

Autonomous stock movement · recall initiation · treating quarantine or unqualified substitutes as available supply.

## Steps

1. `packages/domain/supply.py` constructs classification types (MR-5).
2. `supply_pack` wraps privacy/authZ the same way as batch and PV.
3. Every option has `status: draft` and `no_side_effects: true`.
4. Quarantine inventory is a hold on every affected option.
5. Logger-versus-pallet dispute is a contradiction with both readings and no excursion verdict.

## Done when

`python -m aegis test` is green; `python -m aegis run --workflow supply --id SH-901` emits a schema-valid pack.
