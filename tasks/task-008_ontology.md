# TASK-008 — Ontology: units, identity, terminology, time, trust

**Goal:** make disagreement describable without collapsing it. Quantities, identifiers, coded terms, timestamps and trust status become typed values with deterministic rules, so Workflow A can abstain instead of converting, merging or guessing.

## Specs to load

`01_specs/features/FR-001` §5 (BR-003, BR-004, BR-005) · `01_specs/data/data_model.md` §1, §4 · master plan §5.2, §29.1, §29.5 · AMB-11.

Nothing else. Do not read FR-002/003 engines. Do not build the batch packager (TASK-009).

## Out of scope

OWL reasoners. Normalisation that prefers one side of a conflict. Graph projection (TASK-015). `Contradiction` / `Gap` / `Abstention` construction — those stay in `packages/domain` (MR-5). Converted numeric values.

## Steps

1. Implement core value types in `packages/ontology/`: `Identifier`, `Quantity`, `TimePoint`, `TrustStatus`, `Coding`, `Authority`.
2. Unit comparison: comparable only under identical unit+system or a mapping with `status = approved` effective at `as_of`; otherwise return `unit_mapping_unapproved`. Never emit a converted number.
3. Identity tiers: SAME (scheme+value+org_namespace) → SAME_BY_MAPPING (approved mapping, cite `mapping_id`) → RELATED (declared edge) → stop. No string similarity. Draft/proposed/superseded/ambiguous mappings are `IdentityConflict`.
4. Terminology: a coding's dictionary version is part of its identity. MedDRA 27.1 and 28.0 are not equivalent.
5. Temporal: source timestamps verbatim; missing timezone stays missing; back-entry flag when `recorded_at` differs from `event_time` by any amount (AMB-11 default).
6. Trust: `untrusted` / `referenced_missing` / `superseded` / `reduced_integrity` cannot ground an assertion.
7. Method version is part of a measurement; different methods are not trended without an approved comparability assessment.

## Acceptance checks

- CQ-2: LR-88 `mg/L` vs spec `ug/mL` is not comparable; no converted value exists.
- Unapproved `interface_mappings.csv` row (`approved=no`) cannot make quantities comparable.
- `NTG|` and `BIOX|` identifiers with the same local string are not `SAME`.
- IDMP `ambiguous_strength_presentation` is `IdentityConflict`, not `SAME_BY_MAPPING`.
- A date `2026-07-20` is emitted as `2026-07-20`.
- Ontology modules import no third-party package and do not construct `Abstention`.

## Test expectations

`tests/unit/test_unit_mapping.py` — AC-FR001-05, CQ-2.
`tests/unit/test_terminology_versions.py` — AC-FR002-06.
`tests/unit/test_temporal_precision.py` — AC-FR004-08, AMB-11.
`tests/unit/test_org_scoped_identity.py` — AC-FR004-11.
`tests/unit/test_local_code_collision.py` — AC-FR004-13.
`tests/unit/test_method_comparability.py` — AC-FR004-12.
`tests/unit/test_identity_tiers.py` — plan §29.1.
`tests/unit/test_trust_status.py` — plan §5.2 trust vocabulary.

## Done when

The tests above pass offline with zero installs, and `python -m aegis test` remains green.
