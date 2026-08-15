# TASK-019 — Regulatory records and commitments

**Goal:** emit schema-valid regulatory advisory packs that retain identity conflicts, per-market labels, candidate deadlines and sequence gaps, with no winner, merge, operative date or classification assertion.

## Specs to load

`specs/features/FR-012` (whole file) · FR-005 AC-FR005-19 re-identification combination · TASK-008 identity tiers already Done.

Do not synthesise a golden record. Do not merge labels. Do not classify variations. Do not treat urgency as a rule input.

## Out of scope

Submission or commitment-met language · sequence renumbering · Azure OpenAI (TASK-030) · evidence store (TASK-033).

## Steps

1. `packages/domain/regulatory.py` constructs classification types (MR-5).
2. RIM versus ERP identity conflict names differing fields and selects no winner.
3. Labels are retained per market with version and approval state.
4. Commitment PMC-88 keeps tracker, letter and relative-to-receipt candidates; no operative date.
5. Missing eCTD sequence is named; sequences are not rewritten.
6. Disputed variation positions are retained without a classification statement.
7. `rule_context()` strips urgency keys from `request_id` derivation.
8. Quasi-identifier combinations below `REIDENTIFICATION_K` are withheld as a combination; fields remain available separately.

## Done when

`python -m aegis test` is green; regulatory packs validate against `advisory_nonexecuting`; inspection-surge bytes match the unurged run.
