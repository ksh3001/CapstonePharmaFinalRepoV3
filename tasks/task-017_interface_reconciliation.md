# TASK-017 — Interface contract reconciliation

**Goal:** reconcile LIMS v1 and v2 without inventing unit, status or version equivalence. Unapproved mappings abstain and emit no converted number.

## Specs to load

`specs/features/FR-011` · ontology units/mappings from TASK-008.

Do not approve mappings. Do not coerce v1 free-text units into UCUM.

## Out of scope

Writing back corrected records · migrating v1 consumers · approving `CRO_LAB_TO_LIMS`.

## Steps

1. Every reconciled record carries its contract version; missing version is a gap, never inferred.
2. `CRO_LAB_TO_LIMS` `approved: no` → abstention `unit_mapping_unapproved`.
3. `unit` and `ucum_code` stay distinct fields; invalid UCUM is reported and the record is kept.
4. `status` and `lifecycleState` are presented per version with no asserted equivalence.
5. E2B_R3 variable date precision is preserved per record.

## Done when

`python -m aegis test` is green; PUB-12 validates and contains no converted number from `1:1_assumed`.
