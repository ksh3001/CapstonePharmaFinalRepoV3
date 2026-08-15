# Traceability and gap audit

**Question this file answers:** is anything unaccounted for? Run before every stage gate. A blank cell is a finding, not a formatting issue.

## 1. Chain integrity

The chain is: **DoD clause → plan section → spec → business rule → acceptance criterion → test → evidence path**.

| Check | Method | Result at v3.5 |
|---|---|---|
| Every BR has ≥1 verifying AC | `business_rules_register.md` gap audit | Pass — 146 rules, 0 orphans |
| Every AC has a test task | `testing/ac_test_plan.md` | Pass — 204 ACs, 204 mapped, 0 silently skipped |
| Every AC is machine-checkable | Manual read for "appropriate", "reasonable", "as needed" | Pass — 0 subjective criteria |
| Every confidence-gated behaviour has a number or a declared Unknown with an owner | `matching_confidence_checklist.md` | Pass — 0 unmarked |
| Every public fixture maps to a feature | `FEATURE_INDEX.md` coverage check | Pass — 15/15 |
| Every fixture's `response_contract` resolves to a schema | `api/api_contracts.md` §1 | Pass — closed by AMB-01 |
| Every inject has an **owning feature** | `FEATURE_INDEX.md` | Pass — 84/84 at dimension level, after FR-012 was created for the orphaned D07 set |
| Every inject has a **business rule or acceptance criterion** naming it | Automated scan of the BR and AC registers | Pass — 81/81 behavioural. The three artefact injects are carried by artefact tests instead. Was 65/84 before BR-125…BR-140; see §3 |
| Every cited inject ID exists | Checked against `data/injects.json` | Pass — the original index cited several IDs that did not match; all corrected |
| Every task has a spec behind it | `02_tasks/task_index.md` | Pass — 35 tasks, 0 speculative |
| Every NFR has a measurement | `nfrs.md` | Pass — 26/26 |
| Generated text cannot reach a regulated field | FR-013 BR-100, BR-101 | Pass by design — proven per fixture by AC-FR013-01 |
| Every component has a maturity label | `poc_vs_production.md` | Pass |

## 2. DoD coverage map

| DoD clause | Where satisfied | Status |
|---|---|---|
| §1 Problem, baseline, no-AI alternative, stop/pivot thresholds | `product/scope.md`; plan §14, §24.4 | Covered |
| §2 Three workflows, contracts, provenance, abstention, audit | FR-001/002/003; `api/api_contracts.md` | Covered |
| §2 Prohibited actions per workflow | BR-007, BR-011, BR-021…BR-023; `data/data_model.md` §5 | Covered |
| §3 Six reproducible commands | Plan §7 | Covered |
| §3 Locked deps or zero-install stdlib mode | NFR-02; TASK-001 stdlib gate | Covered |
| §3 Requirements → architecture → ADR → code → test → evidence | This file; `traceability.csv` seeded at TASK-001 | Covered |
| §3 Brownfield coexistence, migration, rollback, decommissioning | Plan §12 | Covered |
| §4 Intended use, GxP boundary, records/signatures boundary | Plan §11; `state_transitions.md` §4 | Covered |
| §4 Nine attack classes tested | Plan §9.4; `tests/security/` | Covered |
| §4 Purpose limitation, minimisation, retention, consent/withdrawal, **pseudonymisation**, re-identification, cross-border | BR-012, **BR-012a**, plan §20.4, injects 059–064 | Covered — pseudonymisation closed in v3.5 |
| §4 Prohibited actions fail closed; execution-time authZ | AP-2, AP-9; `state_transitions.md` §2, §6 | Covered |
| §5 Golden, edge, adversarial, subgroup, failure, outage, recovery, regression | Plan §9.4, §25 | Covered — "golden" is satisfied by property graders, since no golden answers ship with the challenge (BS-08) |
| §5 Measurable release thresholds that block | `evals/thresholds.yaml`; plan §9.5 | Covered |
| §5 SLI/SLO, capacity, observability, incident, backup/restore, AI-disabled continuity, retirement | Plan §13, §24; NFR-12, NFR-17 | Covered |
| §5 Token/context budgets, avoided inference, human-review cost, cost per successful task | Plan §24.4; NFR-07, NFR-08 | Covered |
| §6 30 artefacts completed or mapped | Plan §3.3 submission bridge | Covered — reconciliation runs each phase |
| §6 Machine-readable test and eval results | `evidence/tests/`, `evidence/quality-gates/` | Covered |
| §6 Manifest with owner, version, status, hash | Plan §3.3 B-3 | Covered |
| §6 No secrets or personal data | NFR-19 | Covered |
| §6 `check_submission_structure.py --final` passes | Plan §3.3, release gate | Covered |
| §7 Defence: happy, edge, attack, outage, recovery, manual paths | Plan Phase 8 | Covered |
| §7 Prove prohibited actions cannot execute | `data_model.md` §5 + negative tests | Covered |
| §7 Go / conditional-go / pivot / pause / stop recommendation | Plan §14 | Covered |

Every clause maps. Mapping is not evidence — status becomes *proven* only when the referenced test runs green and writes to `evidence/`.

## 3. Known open items, carried deliberately

| Item | Why it is open | When it closes |
|---|---|---|
| Declared Unknowns AMB-05a, 05b, 11, 12 | Need a human with domain authority, not a decision the team can make from the evidence | Human-review panel, Phase 6 |
| FR-004, FR-008 and FR-012 have no public fixture | The challenge supplies none for these behaviours. Scenarios are team-derived from `data/` | Never fully — reported as team-derived rather than fixture-verified |
| Stage-2 spec approval | Requires the accountable role to review. An AI-authored spec that approves itself defeats the gate | Before Phase 1 implementation begins |
| Cosmos Gremlin adapter | Optional cloud path; not required by any fixture | Only if a cloud demonstration is requested |

### The inject-coverage audit and how it was closed

An automated scan of the registers found that "all 84 injects map to a feature" was true only at **dimension level**. Nineteen injects had an owner and a `TC-INJ` row with a test class in plan §15, but no business rule and no acceptance criterion — so nothing in the authoritative spec set told an implementer what to build or a test what to assert. Sixteen were behavioural gaps inside features that already existed; three were artefact obligations.

| Inject | Dimension | Title | Closed by |
|---|---|---|---|
| 001 | D01 | Board compression target | Artefact test — `docs/product/business-case.md` |
| 002 | D01 | Conflicting success metrics | Artefact test — `docs/product/success-metrics.md` |
| 003 | D01 | No-AI challenge | Artefact test — `docs/product/no-ai-baseline.md` |
| 004 | D01 | Patent-cliff urgency | BR-135 / AC-FR005-17 — reclassified from artefact to behaviour |
| 005 | D01 | Acquisition integration | BR-129 / AC-FR004-11 |
| 007 | D02 | Assay drift | BR-130 / AC-FR004-12 |
| 008 | D02 | Compound genealogy collision | BR-131 / AC-FR004-13 |
| 010 | D02 | Preclinical image manipulation concern | BR-132 / AC-FR004-14 |
| 011 | D02 | Unqualified research model | BR-136 / AC-FR005-18 |
| 012 | D02 | Target-evidence conflict | BR-133 / AC-FR004-15 |
| 015 | D03 | Randomisation service outage | BR-137 / AC-FR009-14 |
| 016 | D03 | Potential unblinding | BR-138 / AC-FR010-12 — the most serious of the nineteen |
| 019 | D03 | Endpoint adjudication backlog | BR-139 / AC-FR010-13 |
| 020 | D03 | Site inspection risk | BR-140 / AC-FR010-14 |
| 026 | D04 | Cleaning validation boundary | BR-125 / AC-FR001-13 |
| 033 | D05 | CAPA effectiveness failure | BR-134 / AC-FR004-16 |
| 042 | D06 | Social-media authenticity | BR-126 / AC-FR002-14 |
| 054 | D08 | Critical excipient shortage | BR-127 / AC-FR003-12 |
| 057 | D08 | Customs documentation mismatch | BR-128 / AC-FR003-13 |

Inject 004 moved from artefact to behaviour deliberately. Plan §15 classed patent-cliff urgency as `T-ARTEFACT`, but urgency invariance is executable — BR-135 now asserts that a request marked urgent produces a byte-identical pack — and a passing test is worth more at a defence than a paragraph in a business case.

### The second pass, found by building the gate

Writing the gate found ten more injects the first pass had missed, because the first scan asked the weaker question — *is this inject named anywhere?* — while the gate asks whether it is named by a rule **and** by a criterion. Nine had a rule whose only verifying criterion tested a different scenario, and one had a criterion but no rule.

| Inject | Title | What was wrong | Closed by |
|---|---|---|---|
| 009 | Omics cohort bias | BR-020 verified only by AC-FR002-10, which tests out-of-scope language | AC-FR002-15 |
| 022 | Sterility excursion | BR-010 verified only by AC-FR001-04, which tests MES genealogy | AC-FR001-14 |
| 027 | PAT drift | Same rule, same criterion | AC-FR001-15 |
| 032 | Unapproved spreadsheet | BR-033 verified by draft-status and effective-period criteria only | AC-FR004-17 |
| 034 | Change-control bypass | BR-032 verified only by AC-FR004-02, which tests hash corruption | AC-FR004-18 |
| 043 | Product-quality and safety link | BR-019 verified only by AC-FR002-03, which tests duplicate candidates | AC-FR002-16 |
| 052 | Serialisation aggregation break | BR-027 mapped to AC-FR003-03, the deny-list criterion — unrelated | AC-FR003-14 |
| 055 | CMO capacity conflict | BR-029 verified only by AC-FR003-04, which tests approvals | AC-FR003-15 |
| 059 | Genomic re-identification | BR-047 verified only by AC-FR005-11, which tests segment entitlement | AC-FR005-19 |
| 069 | Ransomware and OT segmentation | An acceptance criterion in FR-014 but no business rule anywhere | BR-141, AC-FR009-15 |

BR-027 is the clearest illustration: a rule about aggregation gaps whose stated verification was the prohibited-verb test. It would have passed every check the spec set had, and shipped unbuilt. **A gate you write is worth more than an audit you run**, because writing it forces the question to be stated precisely enough to be wrong.

### The allow-list, and the gate that enforces it

A standing rule in a register is not a control. The scan that found this gap is therefore made permanent as the **inject-coverage gate** (TASK-001 step 8), which reads `data/injects.json`, scans the inject column of both registers, and fails the build naming any inject not carried by at least one business rule and one acceptance criterion.

The allow-list is closed at three entries and lives at `quality/static-analysis/inject_coverage_allowlist.json`:

| Inject | Artefact | Verifying test |
|---|---|---|
| 001 | `docs/product/business-case.md` | `tests/compliance/test_benefit_claims.py` |
| 002 | `docs/product/success-metrics.md` | `tests/compliance/test_metric_conflicts.py` |
| 003 | `docs/product/no-ai-baseline.md` | `tests/compliance/test_no_ai_baseline.py` |

Two properties make the exemption honest. The gate fails if the allow-list holds any ID beyond these three, so an inconvenient finding cannot be silenced by adding a line — widening the list is a reviewed change that must be argued. And an allow-listed inject is not unverified: each still has an artefact test that fails the build if its document stops saying what it claims.

The gate also fails if either register cites an inject ID that does not exist in `data/injects.json`, which is the defect the v3.5 pass had to correct by hand.

**Standing rule.** Dimension ownership is not coverage. The check that matters is whether an inject is named by a rule and a criterion, and from TASK-001 it is enforced by the build rather than asserted here.

**Why Phase 0 and not later.** The existing controls would not have caught this. The release gate in plan §9.5 checks execution results in Phase 7, long after the behaviour was built or omitted, and would pass on a `TC-INJ` test written from a one-line §15 summary. The `stop` hook only reminds, and fails open. Nothing structural stood between a missing rule and a shipped gap.

## 4. Findings closed in v3.5

| Finding | Fix |
|---|---|
| `specs/` and `tasks/` referenced by §30.1, `01_specs/README.md` and TASK-001 but absent from the §2 structure | Added to §2; structure manifest would otherwise have drifted on first commit |
| Pseudonymisation named by DoD §4 with no rule, AC or test anywhere in the spec set | BR-012a + AC-FR002-13 + `tests/security/test_pseudonymisation.py` |
| `poc_vs_production.md` required by plan §30.3 but never authored | Authored |
| No data model or state-transition specs, both core technical-design contracts | `data/data_model.md`, `data/state_transitions.md` authored |
| NFRs scattered across plan §13, §24, §9.5 with no single measurable register | `nfrs.md` authored, 20 rows each with a measurement |
| PUB-12 filed under FR-009 "continuity" although it is a LIMS v1-versus-v2 interface reconciliation | Split into **FR-011**; a spec written under the wrong feature would not have matched the fixture |
| Dimension D07 — injects 045 to 050 — had no owning feature | **FR-012** authored; the injects were mapped to test classes but no feature claimed the behaviour |
| Feature index cited inject IDs that did not exist or meant something else | All IDs verified against `data/injects.json` and corrected across every spec |
