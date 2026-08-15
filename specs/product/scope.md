# Product scope and architecture principles

**Question this file answers:** what problem are we solving, what is in and out of scope, and which principles bind every downstream decision.

It deliberately contains no endpoints, screens or data models. Those live in the feature specs and technical design.

## 1. Problem

NovaCura staff in three regulated workflows spend their scarce expert time assembling evidence rather than judging it. Batch evidence sits across MES, LIMS and QMS with genuine contradictions; PV intake arrives in multiple languages with duplicate cases and competing reporting clocks; supply disruptions need options assembled under constraints that change hourly. The cost of a wrong judgement is patient harm or regulatory exposure, so the answer cannot be an automation that decides faster.

**AEGIS assembles the evidence and states honestly what it cannot resolve.** A qualified human decides, every time.

## 2. Intended use

Advisory evidence assembly for authorised reviewers in three workflows: GxP batch evidence reconciliation, pharmacovigilance intake and signal support, and supply shortage / cold-chain option generation. Outputs are working drafts for human review, not regulated records.

## 3. In scope

Evidence retrieval with provenance · contradiction detection · gap identification · abstention with reasons · duplicate and linkage *candidates* for human confirmation · bounded provenance traversal · draft supply options with constraints and approval paths · policy and trust gates · audit trail · human-review console · evaluation and coverage reporting.

## 4. Out of scope — permanently, not "later"

Batch disposition or release · final PV causality, seriousness, expectedness or reportability · clinical eligibility decisions · stock reservation, allocation or shipment · quality-status change · recall initiation · regulatory submission · any write to a system of record · electronic signatures.

These are not backlog items. A feature request in this list is rejected by design review and by the runtime policy gate, and introducing one invalidates the EU AI Act applicability analysis (master plan §23.3).

## 5. Architecture principles

Numbered so that specs, reviews and ADRs can cite them.

| ID | Principle |
|---|---|
| **AP-1** | Deterministic engines are the source of truth. The agent sequences work; it never decides. |
| **AP-2** | Deny by default, checked at execution time. Stale, ambiguous or unverifiable state denies. |
| **AP-3** | Evidence is preserved verbatim with its source, authority, effective date, precision and units. Disagreement is described, never normalised away. |
| **AP-4** | Abstention is a successful outcome. An honest "cannot resolve, here is why" outranks a confident answer. |
| **AP-5** | The assessed path installs nothing and runs offline. |
| **AP-6** | Every third-party capability sits behind a port and a runtime mode, so it can be removed without touching the core. |
| **AP-7** | Regulated outputs are closed contracts. Anything that does not fit goes to a separate artifact, never into a schema extension. |
| **AP-8** | The knowledge graph is a read-only projection rebuilt from source, never a system of record. |
| **AP-9** | Authorisation, consent, residency and legal-hold state are never cached. |
| **AP-10** | The UI is a pure consumer. No business rule exists below the API. |
| **AP-11** | Every claim is wired to a test, so a claim that stops being true fails the build. |
| **AP-12** | Determinism is a design constraint. Identical inputs produce identical bytes. |

## 6. Users and authority

Seven runtime roles. The first five are the primary business users; `auditor` and `unblinding_authority` are required by FR-008, FR-014 and BR-138 respectively. Entitlements, the sensitive-segment matrix, role-name canonicalisation and the segregation-of-duties constraints are specified in `../registers/roles_and_entitlements.md`, which is authoritative — this table is the summary.

| Role | Uses | Never delegates |
|---|---|---|
| EU Qualified Person | Batch evidence readiness | Release decision |
| Safety physician | PV intake packs, duplicate candidates | Causality, seriousness, reportability |
| Supply governance board | Draft options and constraints | Allocation and shipment |
| Quality reviewer | Contradictions, gaps, provenance | Disposition |
| CISO / DPO | Gate results, privacy findings | Consent and residency determinations |
| Auditor / inspector | Any pack and evidence chain in scope, read-only | Every interrupt — satisfies none |
| Unblinding authority | Potential-unblinding findings | Unblinding itself; receives no allocation value |

These are distinct from the six **accountability roles** in plan §26, which own the build and hold no runtime entitlement.

## 7. Success measures

Cycle time to a reviewable evidence pack · proportion of contradictions surfaced rather than missed · abstention correctness · zero prohibited outputs · reviewer trust measured by the human panel · cost per successful task including human review time.

Explicitly **not** a success measure: model accuracy leadership, or automation rate.

## 8. Assumptions

Synthetic package data stands in for source systems · human review remains meaningful rather than rubber-stamped · the EU deployer lens is sufficient for this analysis · role names are binding while individual names remain pending (A-001).

## 9. Open questions

Tracked in `../registers/spec_ambiguities.md`. None currently block Phase 0 or Phase 1.
