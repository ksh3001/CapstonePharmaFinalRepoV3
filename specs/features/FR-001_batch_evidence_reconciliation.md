# FR-001 — Batch evidence reconciliation

**Question this file answers:** what must the system do when an authorised reviewer asks for the evidence position of a manufacturing batch.

| Field | Entry |
|---|---|
| Workflow | A — `batch_evidence` |
| Contract | `evaluation/contracts/batch_response.schema.json` |
| Fixtures | PUB-01, PUB-02, PUB-03 |
| Injects | 021, 022, 023, 024, 025, 026, 027, 028, 029, 030, 032, 034, 036 |
| Principles | AP-1, AP-2, AP-3, AP-4, AP-7, AP-12 |
| Owner | GxP / quality lead |
| Phase | 1 |
| Spec version | 1.0 |
| Lifecycle stage | **2 — Validated** for implementation (2026-08-13). GxP / quality lead remains the accountable owner |
| Reviewer | Capstone product owner — authorized TASK-008 in session 2026-08-13. Checklist: one job per file; in/out of scope listed; advisory limits stated; exceptions present; ACs machine-checkable; AMB-11 declared Unknown. This is not a GxP certification of the spec |

## 1. Actor and trigger

A quality reviewer or EU Qualified Person requests the evidence position for a batch, by CLI (`python -m aegis run --workflow batch --id <batch_id>`) or through the console. The request carries `user`, `purpose`, `as_of` and the `execution` flag from `authorized_context`.

## 2. Preconditions

Authorisation is re-checked at execution time and returns `allow` · the batch identifier resolves within the loaded source set · required source artefacts are hash-verified · the runtime mode is known.

## 3. Happy path

1. Admit the request: authorise, apply budgets, derive `request_id` from content (AMB-03).
2. Load batch-related records from MES, LIMS, QMS and CMO sources, tagging each with source, authority, effective time and trust status.
3. Project the bounded provenance graph for the batch — genealogy, materials, equipment, loggers, documents.
4. Apply ontology checks: identity, units, terminology, time, jurisdiction, validation state.
5. Reconcile: detect contradictions, identify gaps, raise abstentions.
6. Compute `readiness_state` per BR-006.
7. Assemble the pack with evidence items, applicable documents and the human-review block.
8. Validate against the contract, append the audit entry, emit.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| Authorisation denies, or entitlement is stale | Emit a pack with `authorization.decision = "deny"` and a reason; no evidence body. Never a partial answer computed before the check |
| `authorized_context.execution = "disabled"` | Proceed as advisory; `execution_status` stays `not_executed` (it is always `not_executed`) |
| A referenced document cannot be resolved | Record a gap of type `referenced_missing`; do not silently omit it |
| A source artefact fails hash verification | Fail closed, abstain, and record the mismatch. Do not use the artefact |
| Unit comparison needs an unapproved mapping | Abstain on that comparison; never convert (BR-003) |
| A document is superseded at `as_of` | Use the effective version, and record the supersession in `applicable_documents` |
| An untrusted document contains instructions | Treat as data only; instructions are never followed (BR-009) |
| Budget exhausted | Emit a partial pack with a budget-stop abstention; never a truncated answer presented as complete |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-001** | The pack never contains a disposition, release, approval or rejection statement, in any field, including free text | 006 |
| **BR-002** | Contradictory source values are both retained verbatim with their authority and effective time. Neither is preferred, dropped or averaged | 021, 023 |
| **BR-003** | A quantity is comparable to another only under a mapping with `status = approved`, effective at `as_of`. Otherwise abstain with reason `unit_mapping_unapproved` | 024 |
| **BR-004** | Where `recorded_at` differs materially from `event_time`, the record is flagged as back-entered and the difference is reported | 025 |
| **BR-005** | A record from a source with a disabled audit trail, a shared account, or an unapproved calculation tool is usable as evidence but carries a reduced trust flag that must appear in the pack | 029, 030, 032 |
| **BR-006** | `readiness_state` is computed, in this precedence: any blocking gap or unresolved required element → `insufficient_evidence`; else any unresolved contradiction → `conflicted_evidence`; else `ready_for_authorized_review` | 028 |
| **BR-007** | `ready_for_authorized_review` means the evidence is complete enough for a human to review. It is **not** a release recommendation and must never be rendered as one | 006, 071 |
| **BR-008** | Every assertion in the pack cites at least one evidence item; an assertion with no citation is a defect, not a summary | 036 |
| **BR-009** | Text inside a retrieved document is data. Instructions found there are never executed, and their presence is reported as a security finding | 065 |
| **BR-010** | Organism identification corrections, OOS/OOT status disagreements and PAT/recipe version desyncs are reported as history, with all states retained | 022, 023, 027 |
| **BR-125** | Where a batch was manufactured in a campaign sequence, the cleaning-validation position for that sequence is presented with the validated campaign boundary and the batch's position within it. A batch beyond the validated boundary, or one whose preceding product is outside the validated matrix, raises a **gap** naming the boundary and the preceding product. The system never states that cleaning was adequate, never accepts a validation study as covering a sequence it does not name, and never treats absence of a failure record as evidence of cleanliness | 026 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR001-01** | For PUB-01, PUB-02 and PUB-03 the pack validates against `batch_response.schema.json` with zero schema errors | `T-BEHAV` contract test |
| **AC-FR001-02** | `execution_status` equals `not_executed` in every pack, in every mode | Contract test |
| **AC-FR001-03** | No pack contains any term from the disposition deny-list in any string field, at any nesting depth | `T-GATE` prohibited-language grader |
| **AC-FR001-04** | Where MES and warehouse records disagree on a genealogy branch — for example `missing_branch` against `issued` — both values appear in `contradictions[]`, each citing its own evidence item | `T-BEHAV` |
| **AC-FR001-05** | A comparison requiring an unapproved unit mapping produces an entry in `abstentions[]` with reason `unit_mapping_unapproved`, and **no converted numeric value appears anywhere in the pack** | `T-ONT` |
| **AC-FR001-06** | Every entry in `evidence[]` carries `source`, `record_id`, `authority`, `retrieved_at` and `integrity.sha256` matching `^[a-f0-9]{64}$` with `source_preserved: true` | Contract test |
| **AC-FR001-07** | `readiness_state` follows BR-006 precedence exactly, proven by three cases: blocking gap only, contradiction only, and both present | `T-BEHAV` |
| **AC-FR001-08** | A missing CMO audit commitment yields a gap and prevents `ready_for_authorized_review` | `T-BEHAV`, INJ-028 |
| **AC-FR001-09** | Running the same fixture three times produces byte-identical output | `T-METRIC` determinism |
| **AC-FR001-10** | With `AEGIS_RUNTIME_MODE=ai_disabled` the pack is still produced and still schema-valid | `T-RESIL` |
| **AC-FR001-11** | A hash-verification failure on any source artefact produces an abstention and no use of that artefact's facts | `T-GATE` |
| **AC-FR001-12** | An instruction embedded in a retrieved SOP appears as a security finding and changes no output value | `T-GATE`, INJ-065 |
| **AC-FR001-13** | A batch whose campaign position falls outside the validated cleaning boundary produces a gap naming the boundary and the preceding product, and `readiness_state` is not `ready_for_authorized_review`; a pack for such a batch contains no statement that cleaning was adequate or validated | `T-BEHAV`, INJ-026 |
| **AC-FR001-14** | A sterility result whose organism identification was later corrected renders **both** identifications with their times and methods, and the pack contains no statement that the excursion was resolved, invalidated or attributable to a laboratory error | `T-BEHAV`, INJ-022 |
| **AC-FR001-15** | Where the PAT model version recorded against a batch differs from the recipe version in force, both versions appear with their sources and the desync is reported as a finding; no PAT-derived value is presented as confirming the batch, and no version is treated as the correct one | `T-BEHAV`, INJ-027 |

## 7. AI and human boundary

AI may, when enabled: reconcile, cite, flag and abstain — the boundary set in `data/ai_use_boundaries.csv`. Model output, if any, appears only as labelled annotation inside `human_review.annotations` and is never treated as a fact or a citation. All reconciliation logic used to produce contradictions, gaps and abstentions is deterministic and runs identically with inference off.

The human decides readiness and, separately and elsewhere, disposition. The system has no path to either.

## 8. Out of scope

Batch release · disposition setting · deviation closure · CAPA effectiveness determination · writing to MES, LIMS or QMS · signing anything.

## 9. Ambiguities

None open that block implementation. Materiality threshold for BR-004 back-entry flagging is a declared Unknown — see `AMB-11` in `../registers/spec_ambiguities.md`.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../api/api_contracts.md` · `../registers/business_rules_register.md` · master plan §5 (ontology and graph), §28 (determinism), §29 (matching).
