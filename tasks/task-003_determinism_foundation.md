# TASK-003 — Canonical serialisation and derived identifiers

**Goal:** make byte-identical output structurally guaranteed rather than hoped for. Everything written after this task depends on it, which is why it comes before any engine.

## Specs to load

`00_plan/MASTER_BUILD_PLAN.md` §28 (all rules) · AMB-03, AMB-04 in §27 · `01_specs/product/scope.md` (AP-3, AP-12).

## Out of scope

Domain content. Evidence assembly. Anything that decides *what* to serialise.

## Steps

1. Implement `packages/kernel/canonical.py`: `dumps()` using `sort_keys=True`, `ensure_ascii=False`, `separators=(",", ":")`, UTF-8, LF, single trailing newline.
2. Implement declared sort helpers for each emitted array type, each with an explicit tiebreaker: evidence by `(source, record_id)`, contradictions by `(topic, source, record_id)`, gaps by `(gap_type, subject_id)`, abstentions by `(reason_code, subject_id)`.
3. Implement `derive_request_id(scenario_id, as_of, input_hash, code_version)` returning `REQ-` plus the first 16 hex characters of the SHA-256.
4. Implement `derived_timestamp(as_of)` for `retrieved_at` and `checked_at`, and a separate `preserve_source_time(value)` that returns the source string **unchanged**, including its precision and any missing timezone.
5. Implement decimal handling: `decimal.Decimal` with a declared rounding mode for computed ratios; a guard that rejects binary floats reaching serialisation.
6. Add the hostile-environment CI job: non-UTC `TZ`, non-English `LANG`, randomised `PYTHONHASHSEED`.

## Acceptance checks

- Serialising the same object graph twice produces identical bytes, including under the hostile environment.
- Reordering the input records does not change the output bytes.
- A `float` reaching serialisation raises rather than rounding silently.
- A source timestamp lacking a timezone is emitted exactly as it arrived — not defaulted to UTC, not widened.
- `derive_request_id` is stable across processes and machines, and changes when any input changes.

## Test expectations

`tests/unit/test_canonical_json.py` — ordering, encoding, float rejection, source-time preservation.
`tests/regression/test_byte_identical.py` — three consecutive runs of a sample pack, no exclusions (AC-FR001-09, AC-FR002-12, AC-FR003-11).

## Done when

The determinism threshold in plan §9.5 can be met with **no excluded fields**, and the hostile-environment job passes.

## Note

If a later task finds itself wanting to exclude a field from the determinism comparison, that is a defect in this task, not a reason to weaken the threshold.
