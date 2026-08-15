# FR-002 — PV intake and signal support

**Question this file answers:** what must the system do when a safety physician asks for an intake pack covering one or more adverse event cases.

| Field | Entry |
|---|---|
| Workflow | B — `pv_intake` |
| Contract | `evaluation/contracts/pv_response.schema.json` |
| Fixtures | PUB-04, PUB-05, PUB-06 |
| Injects | 009, 037, 038, 039, 040, 041, 042, 043, 044, 062, 072 |
| Principles | AP-1, AP-3, AP-4, AP-9, AP-12 |
| Owner | Safety physician role, with domain lead |
| Phase | 3 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Stage 2 validation must resolve AMB-05a |
| Reviewer | Pending |

## 1. Actor and trigger

A safety physician or PV operations user requests an intake pack for a case set, by CLI or console, with `user`, `purpose`, `as_of` and the execution flag.

## 2. Preconditions

Authorisation returns `allow` for a PV purpose · the requested case identifiers resolve · consent, residency and legal-hold state are evaluated live, never from cache (AP-9) · source artefacts are hash-verified.

## 3. Happy path

1. Admit and authorise; evaluate privacy state for the case set.
2. Extract source facts from each case record, preserving the original language and verbatim values.
3. Normalise only what the ontology permits — never a clinical judgement.
4. Compute duplicate candidates per the fixed strategy in §5 BR-014.
5. Reconstruct every reporting clock from its own awareness evidence.
6. Record terminology codings with the MedDRA version in force for each.
7. Assemble listedness context per jurisdiction, without concluding expectedness.
8. Determine required reviews, assemble, validate, audit, emit.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| Consent purpose does not cover the request | Deny, with reason; no case content in the pack |
| Legal hold conflicts with a deletion request | Restrict and escalate; never delete, never silently comply |
| Case language is outside validated scope | Abstain on extraction for that case, flag the subgroup limitation, and escalate for human translation |
| A case lacks minimum reporting criteria | Report the gap; never infer the missing element |
| Two MedDRA versions apply across the set | Retain both codings with their versions; group version-aware |
| Source is social media or unverified | Flag authenticity uncertainty; never auto-submit or auto-classify |
| Residency rules block a cross-border read | Deny that source and report the restriction |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-011** | The pack never states causality, seriousness, expectedness or reportability as a conclusion. Those fields belong to the human | 006, 040, 044 |
| **BR-012** | Personal data is minimised to what the stated purpose requires; free-text excess is redacted and the redaction is recorded | 062 |
| **BR-012a** | Direct identifiers are replaced by a **deterministic pseudonym** derived from the identifier plus a per-purpose salt, so the same subject is linkable within a purpose and not across purposes. The mapping is never emitted in a pack, and pseudonymisation is recorded as a transformation in the audit trail — it is a protective measure, not anonymisation, and the data remains personal data | 059, 062 |
| **BR-013** | Every reporting clock is reconstructed from its own awareness evidence and all candidate clocks are retained with their sources. The system does not pick one | 038 |
| **BR-014** | Duplicate candidates follow the fixed strategy in master plan §29.2 — exact worldwide-unique-id, then a six-field composite with a ±7-day onset window, scored by matched-field count, surfaced at ≥3, never merged at any score | 037 |
| **BR-015** | Each terminology coding carries the dictionary version used. Codings from different versions are never silently pooled | 039 |
| **BR-016** | Listedness context is presented per jurisdiction with its source document, and the sources' disagreement is preserved | 040 |
| **BR-017** | Sensitive segments — pregnancy, paediatric, genomic — are role-gated and absent from packs for roles without entitlement | 041 |
| **BR-018** | Signal statistics are advisory context only; no signal is confirmed, prioritised or dismissed | 044 |
| **BR-019** | Cross-domain links to batches or complaints follow master plan §29.3 and default to an `unconfirmed_link` abstention | 043 |
| **BR-020** | Subgroup quality limitations, including language, are stated in the pack rather than hidden in documentation | 072, 009 |
| **BR-126** | A report drawn from social media or another unverifiable channel is presented with each of the four minimum criteria — identifiable reporter, identifiable patient, suspect product, event — marked **present, absent or unverifiable** against its own evidence. `unverifiable` is never collapsed into `absent`, because the two lead a human to different actions. The pack states that validity is undetermined, and no report is submitted, discarded, deduplicated against a validated case or counted in any statistic on the strength of an unverifiable field | 042 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR002-01** | PUB-04, PUB-05 and PUB-06 packs validate against `pv_response.schema.json` with zero errors | Contract test |
| **AC-FR002-02** | No pack contains a causality, seriousness, expectedness or reportability conclusion in any field | `T-GATE` deny-list |
| **AC-FR002-03** | `duplicate_candidates[]` entries list matched and mismatched fields and the score; no case pair is ever merged, and no field named `merged`, `master_case` or equivalent exists | `T-BEHAV`, INJ-037 |
| **AC-FR002-04** | A case pair scoring 2 or below does not appear as a candidate; a pair scoring 3 appears as `duplicate_candidate_weak`; boundary cases at 3 and 4 are both tested | `T-BEHAV` boundary |
| **AC-FR002-05** | `clock_evidence[]` contains every candidate clock with its awareness source; no single clock is presented as *the* clock | `T-BEHAV`, INJ-038 |
| **AC-FR002-06** | `terminology[]` retains the MedDRA version per coding; a set spanning 27.1 and 28.0 produces version-aware grouping and no pooled count | `T-ONT`, INJ-039 |
| **AC-FR002-07** | `listedness_context[]` is jurisdiction-qualified and cites IB, CCDS or local label per entry | `T-ONT`, INJ-040 |
| **AC-FR002-08** | A request whose purpose is not covered by consent is denied before any case content is loaded | `T-GATE`, INJ-060 |
| **AC-FR002-09** | A deletion request conflicting with a legal hold produces restriction and escalation, never deletion | `T-GATE`, PUB-11 |
| **AC-FR002-10** | An out-of-scope language case abstains and records the subgroup limitation | `T-METRIC`, INJ-072 |
| **AC-FR002-11** | A role without sensitive-segment entitlement receives a pack with those segments absent, and their absence is stated | `T-GATE`, INJ-041 |
| **AC-FR002-12** | Three consecutive runs are byte-identical; `ai_disabled` still produces a valid pack | Determinism, `T-RESIL` |
| **AC-FR002-13** | No direct identifier appears in an emitted pack; the same subject yields the same pseudonym within a purpose and a different one across purposes; the pseudonym mapping never leaves the kernel; the transformation is recorded in the audit trail | `T-GATE`, INJ-062 |
| **AC-FR002-14** | A social-media sourced report renders all four minimum criteria with one of exactly three states, and a criterion backed by no evidence renders `unverifiable` rather than `absent`; the pack carries no submission, discard or duplicate-merge outcome for that report, and it contributes to no count | `T-BEHAV`, INJ-042 |
| **AC-FR002-15** | Where a cohort under-represents a population relative to the population the question concerns, the pack states the limitation with the affected subgroup named and the comparison that revealed it, and every statistic derived from that cohort carries the limitation; no finding generalises beyond the represented population | `T-METRIC`, INJ-009 |
| **AC-FR002-16** | A complaint, batch and ICSR sharing an identifier within the linkage window appear as an `unconfirmed_link` candidate carrying the shared identifier and the time distance; the pack asserts no causal or quality relationship between them, and the candidate is absent where the window is exceeded | `T-KG`, INJ-043 |

## 7. AI and human boundary

AI may, when enabled: extract, normalise within ontology limits, cluster candidates, and cite. It may not conclude. Every clustering decision that reaches the pack is reproducible by the deterministic rule set, so the pack is unchanged with inference off.

## 8. Out of scope

Case merging · causality assessment · seriousness or expectedness determination · regulatory submission · narrative authoring for submission · signal confirmation.

## 9. Ambiguities

`AMB-05a` — the ±7-day window and the 3/4 score cut points are team-set POC defaults awaiting safety-physician confirmation. Recorded with owner in `../registers/spec_ambiguities.md`; implementation proceeds with the defaults surfaced as configuration.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../api/api_contracts.md` · `../registers/matching_confidence_checklist.md` · master plan §29.2, §29.3, §28.
