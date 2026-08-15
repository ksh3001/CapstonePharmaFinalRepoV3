# Feature index

One feature per file. All fourteen are authored; none has passed stage 2, so no task may be cut against a feature yet.

| FR | Feature | Workflow | Fixtures | Key injects | Phase | Status |
|---|---|---|---|---|---|---|
| **FR-001** | Batch evidence reconciliation | A | PUB-01, 02, 03 | 021, 022, 023, 024, 025, 028, 029, 036 | 1 | Authored |
| **FR-002** | PV intake and signal support | B | PUB-04, 05, 06 | 037, 038, 039, 040, 041, 042, 043, 044 | 3 | Authored |
| **FR-003** | Supply options and cold-chain recovery | C | PUB-07, 08 | 051, 052, 053, 054, 055, 056, 057, 058 | 3 | Authored |
| **FR-004** | Evidence provenance and integrity | Shared | all | 013, 029, 031, 032, 034, 036, 048, 065 | 0–1 | Authored |
| **FR-005** | Policy, trust and privacy gates | Shared | PUB-09, 11 | 006, 017, 030, 035, 041, 059–064, 066, 067, 068, 070 | 2 | Authored |
| **FR-006** | Agent orchestration and human-in-the-loop | Shared | PUB-13 | 006, 056, 065, 076, 079, 080, 081, 082 | 4 | Authored |
| **FR-007** | FinOps budgets and cost reporting | Shared | PUB-14 | 075, 076, 077, 078 | 6 | Authored |
| **FR-008** | Human review console | Shared | none | 006, 063, 071, 072, 073, 074, 079 | 5 | Authored — live HTMX console implemented |
| **FR-009** | Continuity and degraded operation | Shared | PUB-10 | 015, 069, 079, 081, 082, 083, 084 | 4 | Authored |
| **FR-010** | Clinical protocol applicability | Shared | PUB-15 | 013, 014, 016, 017, 018, 019, 020 | 3 | Authored |
| **FR-011** | Interface contract and unit reconciliation | Shared | PUB-12 | 023, 024, 025, 045 | 2 | Authored |
| **FR-012** | Regulatory records, identity and commitments | Shared | none | 045, 046, 047, 048, 049, 050 | 3 | Authored |
| **FR-013** | AI advisory generation and grounding (Azure OpenAI) | Shared | all, in `advisory` mode | 064, 065, 070, 075, 076, 078, 079, 081, 082 | 4 | Authored |
| **FR-014** | Evidence store, integrity and retention | Shared | all | 029, 035, 036, 061, 062, 069, 083, 084 | 1, 4 | Authored |

## Coverage check

**Fixtures.** Every public fixture maps to a feature: PUB-01/02/03 → FR-001 · PUB-04/05/06 → FR-002 · PUB-07/08 → FR-003 · PUB-09 → FR-005 · PUB-10 → FR-009 · PUB-11 → FR-005 · PUB-12 → FR-011 · PUB-13 → FR-006 · PUB-14 → FR-007 · PUB-15 → FR-010. Fifteen of fifteen.

**Azure OpenAI.** FR-013 is the **only** feature in which a model runs. Every other feature is deterministic in every mode. FR-013 writes to `human_review.annotations` and nowhere else, so the regulated fields of all fifteen fixtures are byte-identical with the model on or off (AC-FR013-01).

**Features without a fixture.** FR-004, FR-008 and FR-012 have no public fixture. Their results are reported as team-derived rather than fixture-verified, and the distinction is preserved in the coverage record. This is a limitation stated openly, not a coverage claim.

**Injects.** All 84 are covered at **rule level**, not merely owned at dimension level: 81 are named by at least one business rule *and* at least one acceptance criterion that verifies that inject, and the remaining three — 001, 002, 003 — are artefact obligations verified by artefact tests in `../testing/ac_test_plan.md`. Closed by BR-125 to BR-141 across two passes; see `../registers/traceability_gap_audit.md` §3. The claim is no longer maintained by hand — the inject-coverage gate (TASK-001 step 8) fails the build if it stops being true. Dimensions and their owners: D01 → FR-005, FR-006 · D02 → FR-001, FR-002, FR-004 · D03 → FR-010 · D04 → FR-001 · D05 → FR-004 · D06 → FR-002 · D07 → FR-011, FR-012 · D08 → FR-003 · D09 → FR-005 · D10 → FR-004, FR-005, FR-006 · D11 → FR-008 · D12 → FR-007 · D13 → FR-006, FR-009. The coverage CSV remains the authoritative record of *results*; this table records *ownership*.

## Corrections made when the specs were authored

Recorded so the reasoning survives.

| Change | Reason |
|---|---|
| PUB-12 moved from FR-009 to a new **FR-011** | PUB-12 reconciles LIMS v1 against v2 with an unapproved unit mapping. That is an interface-contract problem, not a continuity problem. Filing it under continuity would have produced a spec that did not match the fixture |
| **FR-012** created | Dimension D07 — IDMP identity, labelling divergence, commitment deadlines, eCTD sequence gaps, variation disputes, inspection surge — had no owning feature. The injects were mapped to test classes but no feature claimed the behaviour, so it would have been built without being specified |
| **FR-013** and **FR-014** added | Azure OpenAI became the advisory model layer and evidence gained a real store. Both are cross-cutting behaviours with their own gates, so neither could live inside an existing feature |
| Inject IDs corrected throughout | The original index cited IDs that did not match `data/injects.json`. Verified against the source: 070 is model supply-chain compromise, not shared accounts (that is 030); 081 is model substitution regression, not budget exhaustion (that is 076); 009 is omics cohort bias, not language inequity (that is 072) |
