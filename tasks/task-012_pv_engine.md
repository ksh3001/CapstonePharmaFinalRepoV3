# TASK-012 — PV engine: source facts, clocks, terminology, listedness

**Goal:** produce schema-valid PV intake packs for PUB-04, PUB-05 and PUB-06 from deterministic rules. No causality, seriousness, expectedness or reportability conclusion. No case merge.

## Specs to load

`specs/features/FR-002_pv_intake_signal_support.md` · `packages/contracts/regulated/pv_response.schema.json` · AMB-05a (already in TASK-011).

Do not implement privacy gates (TASK-013). Do not implement cross-domain `unconfirmed_link` (TASK-016 / AC-FR002-16). Do not use `duplicate_candidates.csv` similarity as the score.

## Out of scope

Causality / seriousness / expectedness / reportability. Case merging. Consent, DSR, residency, sensitive-segment and pseudonymisation gates. Signal confirmation.

## Steps

1. Source facts are verbatim per case. Cases are never merged.
2. Every reporting clock is retained with its source. The pack does not pick one.
3. Each MedDRA coding carries its version. 27.1 and 28.0 stay distinct; no pooled count.
4. Duplicate candidates come from TASK-011. Sparse PUB-04 fields may yield none; that is correct.
5. Listedness is jurisdiction-qualified (IB / CCDS / local label). Source disagreement is preserved without an expectedness conclusion.
6. English and German are in validated extraction scope; Arabic and Hindi abstain and name the subgroup (INJ-072).
7. Social-media reports render the four minimum criteria as present / absent / unverifiable. `unverifiable` is not collapsed to `absent`. Validity is undetermined; no submit / discard / merge.
8. Cohort under-representation is named with the comparison (Group-B vs Group-A). Statistics carry the limitation.

## Test expectations

- `tests/contract/test_pv_contract.py` — AC-FR002-01, AC-FR002-06 pack retention
- `tests/integration/test_pv_clocks.py` — AC-FR002-05
- `tests/integration/test_listedness.py` — AC-FR002-07
- `tests/subgroup/test_language_scope.py` — AC-FR002-10
- `tests/integration/test_report_validity_criteria.py` — AC-FR002-14
- `tests/integration/test_cohort_representation.py` — AC-FR002-15

CLI: `python -m aegis run --workflow pv --id PV-1001`

## Done when

PUB-04/05/06 validate against `pv_response.schema.json`; three consecutive dumps match; `python -m aegis test` is green.
