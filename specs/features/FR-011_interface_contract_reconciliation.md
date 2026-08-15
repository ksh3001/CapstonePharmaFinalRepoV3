# FR-011 — Interface contract and unit reconciliation

**Question this file answers:** how the same measurement, arriving under two different API contracts with two different unit conventions, is reconciled without inventing equivalence.

Authored because PUB-12 had no honest home. It was filed under continuity in the original index, but a LIMS v1-versus-v2 reconciliation is not an outage problem.

| Field | Entry |
|---|---|
| Workflow | Shared — feeds A and B |
| Contract | `advisory_nonexecuting.schema.json` for PUB-12 |
| Fixtures | PUB-12 (integration) |
| Injects | 023, 024, 025, 045 |
| Principles | AP-3, AP-4, AP-7, AP-12 |
| Owner | Integration lead, with GxP lead |
| Phase | 2 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

An integration or quality user asks to reconcile results arriving from two versions of the same interface.

## 2. Preconditions

Contract version records and interface mappings are readable and hash-verified · both contract documents are available · the approved-mapping register is readable.

## 3. Happy path

1. Identify the contract version of every incoming record. A record without a declared version is not assumed to be either version.
2. Map fields per version — `unit` against `ucum_code`, `status` against `lifecycleState`, `value` against `numericValue`.
3. Validate unit codes against UCUM where the contract requires UCUM.
4. Check any unit conversion against the approved-mapping register.
5. Where the mapping is unapproved, **abstain on the comparison** and emit both values in their own units.
6. Present status values as source-system values, per version, without a merged vocabulary.
7. Preserve date semantics per contract, including variable precision.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| A conversion rule is present but `approved` is `no` — `CRO_LAB_TO_LIMS`, `mg/L` → `ug/mL`, `1:1_assumed` | Abstain with `unit_mapping_unapproved`. **No converted value appears anywhere in the pack**, not even as an illustration. An unapproved assumption printed once becomes a number someone quotes |
| A unit is free text under v1 and UCUM under v2 | Both retained in their own form; free text is not coerced into a UCUM code |
| A UCUM code fails validation | Reported as an invalid code; the record is not silently dropped and not repaired |
| Status vocabularies differ between versions | Presented per version with the source value. No cross-version status equivalence is asserted without an approved mapping |
| Contract version is missing on a record | Gap raised. The record is not attributed to a version by field-shape guessing |
| Date semantics are declared variable — E2B_R3 | Precision preserved per record; no date is expanded, truncated or given a timezone |
| A field exists in one version and not the other | Reported as a coverage difference, not as a null value |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-086** | Every record carries its contract version through to the pack. Version is part of the fact, not transport metadata | 045 |
| **BR-087** | A unit conversion occurs only under a mapping that is approved and effective at `as_of`. Otherwise the comparison abstains and both values are shown in their source units | 024 |
| **BR-088** | An unapproved converted value is never emitted, in any field, including examples, summaries and annotations | 024 |
| **BR-089** | Unit codes are validated where the contract requires a coding system, and validation failure is reported rather than repaired | 024 |
| **BR-090** | Status values are source-system values, presented per version. Cross-version equivalence requires an approved mapping and is otherwise a contradiction | 023 |
| **BR-091** | Date semantics follow the contract, and declared variable precision is preserved per record | 025 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR011-01** | The PUB-12 pack validates against `advisory_nonexecuting.schema.json` with zero errors | Contract test |
| **AC-FR011-02** | The `CRO_LAB_TO_LIMS` mapping with `approved: no` produces an abstention with reason `unit_mapping_unapproved` | `T-ONT`, PUB-12, INJ-024 |
| **AC-FR011-03** | **No numeric value derived from the `1:1_assumed` rule appears anywhere in the serialised pack**, verified by searching rendered strings, not fields | `T-GATE`, PUB-12, INJ-024 |
| **AC-FR011-04** | Both `mg/L` and `ug/mL` values are presented in their source units, each with its source record | `T-BEHAV`, PUB-12 |
| **AC-FR011-05** | Every reconciled record states its contract version, `v1` or `v2`, in the pack | `T-BEHAV`, PUB-12, INJ-045 |
| **AC-FR011-06** | `unit` and `ucum_code` are treated as distinct fields with distinct semantics; a v1 free-text unit is never emitted as a UCUM code | `T-ONT`, PUB-12 |
| **AC-FR011-07** | `status` and `lifecycleState` values are presented per version with no asserted equivalence | `T-ONT`, PUB-12, INJ-023 |
| **AC-FR011-08** | An invalid UCUM code is reported as invalid, and the record is neither dropped nor corrected | `T-BEHAV`, INJ-024 |
| **AC-FR011-09** | A record with no declared contract version raises a gap and is not assigned a version by inference | `T-GATE`, PUB-12 |
| **AC-FR011-10** | The E2B_R3 declaration of variable date precision results in per-record precision preservation, proven with a date-only and a full-timestamp record | `T-ONT`, PUB-12, INJ-025 |
| **AC-FR011-11** | Three consecutive runs byte-identical; `ai_disabled` still produces a valid pack | Determinism, `T-RESIL` |

## 7. AI and human boundary

No model maps a field, converts a unit, validates a code or asserts equivalence between vocabularies. Mapping is deterministic and register-driven, because a plausible-looking conversion is precisely the failure this feature exists to prevent. Approving a new mapping is a human act recorded in the register.

## 8. Out of scope

Approving unit mappings · amending interface contracts · writing back corrected records · normalising vocabularies · migrating v1 consumers to v2.

## 9. Ambiguities

None blocking. The approved-mapping register is team-authored for the challenge data and is labelled as such wherever it is cited.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../data/data_model.md` §1 · master plan §5.2 (ontology), §28 (determinism).
