# Acceptance criteria register

Every AC from the authored feature specs, with the inject and fixture it defends. Test mapping lives in `../testing/ac_test_plan.md`; this register is the completeness check.

## FR-001 — Batch evidence reconciliation

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR001-01 | Packs schema-valid | T-BEHAV | PUB-01/02/03 |
| AC-FR001-02 | `execution_status = not_executed` always | T-GATE | all |
| AC-FR001-03 | No disposition language, any depth | T-GATE | INJ-006 |
| AC-FR001-04 | Genealogy contradiction retains both values | T-BEHAV | INJ-021 |
| AC-FR001-05 | Unapproved unit mapping abstains, no converted number | T-ONT | INJ-024 |
| AC-FR001-06 | Evidence provenance and hash complete | T-BEHAV | INJ-036 |
| AC-FR001-07 | `readiness_state` precedence proven on three cases | T-BEHAV | INJ-028 |
| AC-FR001-08 | Missing CMO commitment blocks readiness | T-BEHAV | INJ-028 |
| AC-FR001-09 | Byte-identical across three runs | T-METRIC | determinism |
| AC-FR001-10 | Valid pack in `ai_disabled` | T-RESIL | INJ-082 |
| AC-FR001-11 | Hash failure abstains and excludes the artefact | T-GATE | INJ-036 |
| AC-FR001-12 | Embedded instruction becomes a finding, changes nothing | T-GATE | INJ-065 |
| AC-FR001-13 | Beyond-boundary campaign position raises a gap; no adequacy statement | T-BEHAV | INJ-026 |
| AC-FR001-14 | Corrected organism ID renders both identifications; no resolution or lab-error claim | T-BEHAV | INJ-022 |
| AC-FR001-15 | PAT/recipe version desync reported; neither version treated as correct | T-BEHAV | INJ-027 |

## FR-002 — PV intake and signal support

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR002-01 | Packs schema-valid | T-BEHAV | PUB-04/05/06 |
| AC-FR002-02 | No causality, seriousness, expectedness, reportability | T-GATE | INJ-006, 040, 044 |
| AC-FR002-03 | Candidates list matched and mismatched fields; no merge field exists | T-BEHAV | INJ-037 |
| AC-FR002-04 | Score boundaries at 3 and 4 tested | T-BEHAV | INJ-037 |
| AC-FR002-05 | All candidate clocks retained | T-BEHAV | INJ-038 |
| AC-FR002-06 | MedDRA version retained; no pooled count | T-ONT | INJ-039 |
| AC-FR002-07 | Listedness jurisdiction-qualified | T-ONT | INJ-040 |
| AC-FR002-08 | Purpose not covered → denied before loading content | T-GATE | INJ-060 |
| AC-FR002-09 | Deletion vs hold → restrict and escalate | T-GATE | PUB-11 |
| AC-FR002-10 | Out-of-scope language abstains with subgroup note | T-METRIC | INJ-072 |
| AC-FR002-11 | Sensitive segments absent for unentitled roles, absence stated | T-GATE | INJ-041 |
| AC-FR002-12 | Determinism and `ai_disabled` | T-METRIC / T-RESIL | INJ-082 |
| AC-FR002-13 | Pseudonymisation deterministic per purpose; mapping never emitted | T-GATE | INJ-062, DoD §4 |
| AC-FR002-14 | Validity criteria tri-state; `unverifiable` never becomes `absent`; no auto-submit or discard | T-BEHAV | INJ-042 |
| AC-FR002-15 | Under-represented cohort stated with subgroup named; no generalisation beyond it | T-METRIC | INJ-009 |
| AC-FR002-16 | Complaint/batch/ICSR link is an `unconfirmed_link` candidate; no causal claim | T-KG | INJ-043 |

## FR-003 — Supply options and cold-chain recovery

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR003-01 | Packs schema-valid | T-BEHAV | PUB-07/08 |
| AC-FR003-02 | All options `draft`; `no_side_effects` true | T-GATE | INJ-056 |
| AC-FR003-03 | No execution verbs anywhere | T-GATE | INJ-006 |
| AC-FR003-04 | Approvals non-empty where stock would move | T-BEHAV | INJ-056 |
| AC-FR003-05 | Quality holds on every affected option | T-BEHAV | INJ-051 |
| AC-FR003-06 | Sensor dispute retained, no excursion verdict | T-KG | INJ-051 |
| AC-FR003-07 | Traversal incompleteness reported honestly | T-KG | INJ-058 |
| AC-FR003-08 | Counterfeit suspicion escalates, no recall language | T-GATE | INJ-053 |
| AC-FR003-09 | Replay is idempotent | T-RESIL | INJ-080 |
| AC-FR003-10 | Stale checkpoint blocks auto-resume | T-GATE | INJ-080 |
| AC-FR003-11 | Determinism and `ai_disabled` | T-METRIC / T-RESIL | INJ-082 |
| AC-FR003-12 | Unqualified substitute described, never counted as supply | T-BEHAV | INJ-054 |
| AC-FR003-13 | Documentation mismatch named field by field; no clearance assertion | T-BEHAV | INJ-057 |
| AC-FR003-14 | Missing aggregation parent is a gap; no parent inferred from proximity or timing | T-KG | INJ-052 |
| AC-FR003-15 | Double-promised CMO capacity shows both commitments; contested capacity never available | T-BEHAV | INJ-055 |

## FR-004 — Evidence provenance and integrity

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR004-01 | Provenance complete on every evidence item | T-BEHAV | all 15 |
| AC-FR004-02 | Corrupted artefact abstains; no fact from it appears | T-GATE | INJ-036 |
| AC-FR004-03 | Draft status never cited as authority | T-BEHAV | INJ-031 |
| AC-FR004-04 | Superseded and superseding both retained | T-BEHAV | INJ-013 |
| AC-FR004-05 | Effective-period exclusion with stated reason | T-ONT | INJ-031 |
| AC-FR004-06 | Injected instruction changes no byte | T-GATE | INJ-065 |
| AC-FR004-07 | Missing reference produces a named gap | T-BEHAV | INJ-048 |
| AC-FR004-08 | Date-only timestamp not expanded | T-ONT | INJ-025 |
| AC-FR004-09 | Back-entry flagged with magnitude, travels downstream | T-BEHAV | INJ-036 |
| AC-FR004-10 | Build fails on `EvidenceItem` built outside the package | T-ARTEFACT | AP-3 |
| AC-FR004-11 | Same identifier from two organisations resolves to two identities | T-ONT | INJ-005 |
| AC-FR004-12 | No trend across a method change without an approved comparability assessment | T-ONT | INJ-007 |
| AC-FR004-13 | Local-code collision reported, neither record made canonical | T-ONT | INJ-008 |
| AC-FR004-14 | Manipulation concern raised and never cleared by a later record | T-BEHAV | INJ-010 |
| AC-FR004-15 | Conflicting sources retained; licence-barred content excluded as a gap | T-KG | INJ-012 |
| AC-FR004-16 | Recurrence linked across taxonomy versions; no effectiveness verdict | T-KG | INJ-033 |
| AC-FR004-17 | Uncontrolled-tool value never cited as authority; dependent conclusions abstain | T-BEHAV | INJ-032 |
| AC-FR004-18 | Change-control bypass is an integrity finding; retrospective approval does not clear it | T-BEHAV | INJ-034 |

## FR-005 — Policy, trust and privacy gates

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR005-01 | Packs schema-valid | T-BEHAV | PUB-09, PUB-11 |
| AC-FR005-02 | Revoked-but-cached contractor denied | T-GATE | PUB-09, INJ-067 |
| AC-FR005-03 | Revocation-lag window reported as a finding | T-BEHAV | PUB-09 |
| AC-FR005-04 | Denial is a valid pack leaking nothing | T-GATE | INJ-006 |
| AC-FR005-05 | Removing the cache does not change the decision | T-GATE | PUB-09 |
| AC-FR005-06 | DSR-17 under LH-44 → restriction, never deletion | T-GATE | PUB-11, INJ-061 |
| AC-FR005-07 | Per-purpose withdrawal honoured; cached consent reported | T-BEHAV | PUB-11, INJ-017 |
| AC-FR005-08 | 90-day log rule applied only absent an evidence hold | T-BEHAV | PUB-11 |
| AC-FR005-09 | Unregistered purpose denied and named | T-GATE | INJ-063 |
| AC-FR005-10 | Cross-border path without lawful basis denied | T-GATE | INJ-064 |
| AC-FR005-11 | Unentitled segment absent from serialised output | T-GATE | INJ-041, 063 |
| AC-FR005-12 | Zero cache keys for authZ, consent, residency, hold | T-SEC | AP-9 |
| AC-FR005-13 | Shared-account approval unattributable; two-device flagged | T-BEHAV | PUB-09, INJ-030 |
| AC-FR005-14 | Unsigned or unlisted tool manifest refused | T-SEC | INJ-066, 070 |
| AC-FR005-15 | Safety-data exfiltration path denied | T-SEC | INJ-068 |
| AC-FR005-16 | Determinism; identical decisions in `ai_disabled` | T-METRIC / T-RESIL | INJ-082 |
| AC-FR005-17 | Urgency fields at extreme values produce a byte-identical pack | T-GATE | INJ-004, 050 |
| AC-FR005-18 | Model outside its documented intended use refused, qualification named | T-GATE | INJ-011, 031 |
| AC-FR005-19 | Quasi-identifier combination below the threshold refused as a combination; fields still individually available | T-GATE | INJ-059 |

## FR-006 — Agent orchestration and human-in-the-loop

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR006-01 | Pack schema-valid | T-BEHAV | PUB-13 |
| AC-FR006-02 | AR-77 at 380 minutes not auto-resumed | T-GATE | PUB-13, INJ-080 |
| AC-FR006-03 | Resume creates no third draft | T-RESIL | PUB-13 |
| AC-FR006-04 | DR-1 and DR-2 reported as drafts with no side effect | T-GATE | INJ-056 |
| AC-FR006-05 | Hash-mismatched checkpoint blocks resume | T-GATE | INJ-080 |
| AC-FR006-06 | Zero personal data in checkpoints | T-SEC | INJ-062 |
| AC-FR006-07 | Budget exhaustion emits a valid partial pack | T-RESIL | INJ-076 |
| AC-FR006-08 | Step outside the declared graph refused | T-GATE | INJ-065 |
| AC-FR006-09 | Retry count never exceeded | T-RESIL | INJ-079 |
| AC-FR006-10 | Runner and model-swap parity, byte-identical | T-METRIC | INJ-081, NFR-13 |
| AC-FR006-11 | Determinism and `ai_disabled` | T-METRIC / T-RESIL | INJ-082 |

## FR-007 — FinOps budgets and cost reporting

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR007-01 | Pack schema-valid | T-BEHAV | PUB-14 |
| AC-FR007-02 | Inference cost reproducible by hand | T-METRIC | PUB-14 |
| AC-FR007-03 | Denominator is successful tasks, not requests | T-METRIC | PUB-14, INJ-077 |
| AC-FR007-04 | Zero review costs treated as missing | T-BEHAV | PUB-14, INJ-077 |
| AC-FR007-05 | Total abstains without review duration | T-BEHAV | PUB-14 |
| AC-FR007-06 | Price shock reported with both values | T-BEHAV | PUB-14, INJ-075 |
| AC-FR007-07 | No estimated or assumed cost figure | T-GATE | PUB-14 |
| AC-FR007-08 | Token ceiling stops rather than truncates | T-RESIL | INJ-076 |
| AC-FR007-09 | Wallet ceiling blocks new runs | T-SEC | INJ-076 |
| AC-FR007-10 | Avoided inference and cache-hit reported truthfully | T-METRIC | INJ-077 |
| AC-FR007-10a | Vendor concentration reported with exit cost | T-BEHAV | INJ-078 |
| AC-FR007-11 | Decimal arithmetic; no binary float serialised | T-METRIC | determinism |
| AC-FR007-12 | Determinism and `ai_disabled` | T-METRIC / T-RESIL | INJ-082 |

## FR-008 — Human review console

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR008-01 | Zero regulated-action controls in the route inventory | T-GATE | INJ-006 |
| AC-FR008-02 | Acknowledge disabled until critical evidence opened | T-UX | INJ-071 |
| AC-FR008-03 | Acknowledgement audited and labelled not-a-signature | T-UX | INJ-071 |
| AC-FR008-04 | Gaps and abstentions visible without expanding | T-UX | INJ-071 |
| AC-FR008-05 | Unentitled segment absent from the payload | T-SEC | INJ-063 |
| AC-FR008-06 | Every claim links to its evidence item | T-UX | AP-3 |
| AC-FR008-07 | Zero axe critical or serious findings | T-UX | INJ-073 |
| AC-FR008-08 | Full keyboard operability with visible focus | T-UX | INJ-073 |
| AC-FR008-09 | RTL and Hindi render; values byte-identical | T-UX | INJ-072 |
| AC-FR008-10 | Degraded state names the runbook; no stale pack | T-RESIL | INJ-079 |
| AC-FR008-11 | Contradiction shown both ways, no resolve control | T-UX | AP-3 |
| AC-FR008-12 | Preparer cannot acknowledge under segregation of duties | T-GATE | INJ-074 |

## FR-009 — Continuity and degraded operation

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR009-01 | Pack schema-valid | T-BEHAV | PUB-10 |
| AC-FR009-02 | Zero-hour tolerance means manual immediately | T-RESIL | PUB-10, INJ-079 |
| AC-FR009-03 | 14-day tolerances continue degraded with a deadline | T-BEHAV | PUB-10 |
| AC-FR009-04 | Empty tolerance read as not specified | T-ONT | PUB-10 |
| AC-FR009-05 | Fallback model not substituted without validation | T-GATE | PUB-10, INJ-081 |
| AC-FR009-06 | Cross-region fallback triggers residency evaluation | T-BEHAV | PUB-10, INJ-064 |
| AC-FR009-07 | Prohibited-action suite passes in every degraded mode | T-GATE | INJ-082 |
| AC-FR009-08 | All three workflows produce packs in `ai_disabled` | T-RESIL | INJ-082 |
| AC-FR009-09 | Kill switch works with all endpoints unreachable | T-RESIL | INJ-082 |
| AC-FR009-10 | Manual runbook exists per workflow, else a gap | T-ARTEFACT | PUB-10 |
| AC-FR009-11 | Outage reconciliation required before resumption | T-BEHAV | INJ-082 |
| AC-FR009-12 | Reproducible with all vendor integrations removed | T-RESIL | INJ-083, 084 |
| AC-FR009-13 | Determinism in every degraded mode | T-METRIC | determinism |
| AC-FR009-14 | Manual outage assignment carries provenance; reconciled, never overwritten | T-RESIL | INJ-015 |
| AC-FR009-15 | Isolated source stale by declaration; incident-window writes unconfirmed; no boundary bridged | T-RESIL | INJ-069 |

## FR-010 — Clinical protocol applicability

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR010-01 | Pack schema-valid | T-BEHAV | PUB-15 |
| AC-FR010-02 | Site-approved 4.1 governs; 5.0 global not local | T-BEHAV | PUB-15, INJ-013 |
| AC-FR010-03 | Obsolete-but-cached 3.2 reported as risk | T-BEHAV | PUB-15 |
| AC-FR010-04 | Pending amendment is a gap | T-GATE | PUB-15 |
| AC-FR010-05 | All three ULN values presented as a contradiction | T-BEHAV | PUB-15, INJ-014 |
| AC-FR010-06 | No eligibility or deviation conclusion, any depth | T-GATE | INJ-014 |
| AC-FR010-07 | Range-dependent outcome shown without ranking ranges | T-BEHAV | PUB-15 |
| AC-FR010-08 | Withdrawn consent withholds data, reported | T-GATE | INJ-017 |
| AC-FR010-09 | Device skew reported, timestamps unadjusted | T-ONT | INJ-018 |
| AC-FR010-10 | Instruction in a protocol extract changes nothing | T-GATE | INJ-065 |
| AC-FR010-11 | Determinism and `ai_disabled` | T-METRIC / T-RESIL | INJ-082 |
| AC-FR010-12 | Allocation absent from the payload for every role; inferential unblinding withheld and escalated | T-GATE | INJ-016 |
| AC-FR010-13 | Pending adjudication excluded from counts; no predicted outcome | T-BEHAV | INJ-019 |
| AC-FR010-14 | Site risk as observations; no score, ranking or inspection call | T-BEHAV | INJ-020 |

## FR-011 — Interface contract and unit reconciliation

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR011-01 | Pack schema-valid | T-BEHAV | PUB-12 |
| AC-FR011-02 | Unapproved mapping abstains | T-ONT | PUB-12, INJ-024 |
| AC-FR011-03 | No `1:1_assumed` value anywhere in rendered output | T-GATE | PUB-12, INJ-024 |
| AC-FR011-04 | Both values shown in source units | T-BEHAV | PUB-12 |
| AC-FR011-05 | Contract version stated per record | T-BEHAV | PUB-12, INJ-045 |
| AC-FR011-06 | Free-text unit never emitted as a UCUM code | T-ONT | PUB-12 |
| AC-FR011-07 | Status vocabularies kept per version | T-ONT | PUB-12, INJ-023 |
| AC-FR011-08 | Invalid UCUM reported, not repaired | T-BEHAV | INJ-024 |
| AC-FR011-09 | Missing contract version is a gap, not a guess | T-GATE | PUB-12 |
| AC-FR011-10 | Variable date precision preserved per record | T-ONT | PUB-12, INJ-025 |
| AC-FR011-11 | Determinism and `ai_disabled` | T-METRIC / T-RESIL | INJ-082 |

## FR-012 — Regulatory records, identity and commitments

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR012-01 | Packs schema-valid | T-BEHAV | team-derived |
| AC-FR012-02 | Identity conflict surfaced, no winner chosen | T-ONT | INJ-045 |
| AC-FR012-03 | Label divergence retained per market, no merge | T-BEHAV | INJ-046 |
| AC-FR012-04 | All candidate deadlines with their basis | T-BEHAV | INJ-047 |
| AC-FR012-05 | Sequence gap named | T-BEHAV | INJ-048 |
| AC-FR012-06 | No variation classification statement | T-GATE | INJ-049 |
| AC-FR012-07 | Urgency changes no byte | T-GATE | INJ-050 |
| AC-FR012-08 | No submission or commitment-met language | T-GATE | deny-list |
| AC-FR012-09 | Source, authority, version, effective date on every fact | T-BEHAV | AP-3 |
| AC-FR012-10 | Determinism and `ai_disabled` | T-METRIC / T-RESIL | INJ-082 |

## FR-013 — AI advisory generation (Azure OpenAI)

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR013-01 | Advisory pack byte-identical to offline minus annotations | T-METRIC | all 15, INJ-082 |
| AC-FR013-02 | Kill switch: valid pack, zero outbound calls | T-RESIL | INJ-082 |
| AC-FR013-03 | Unsupported number discarded (G-3) | T-GATE | INJ-024 |
| AC-FR013-04 | Unresolvable citation discarded (G-2) | T-GATE | INJ-065 |
| AC-FR013-05 | Deny-list language discarded (G-1) | T-GATE | INJ-006 |
| AC-FR013-06 | Narrating past an abstention discarded (G-5) | T-GATE | AP-4 |
| AC-FR013-07 | Injection reaches neither prompt nor output | T-GATE | INJ-065 |
| AC-FR013-08 | Zero direct identifiers in stored prompts | T-SEC | INJ-062 |
| AC-FR013-09 | Residency mismatch blocks the call | T-SEC | INJ-064 |
| AC-FR013-10 | No API key anywhere; fails closed without managed identity | T-SEC | INJ-070 |
| AC-FR013-11 | Deployment, version, api-version, fingerprint recorded | T-BEHAV | INJ-081 |
| AC-FR013-12 | Floating model alias fails the build | T-ARTEFACT | INJ-081 |
| AC-FR013-13 | Cassette replay deterministic; zero live calls in evals | T-METRIC | NFR-21 |
| AC-FR013-14 | 429 then 503 degrades to no narrative within retry bounds | T-RESIL | INJ-079 |
| AC-FR013-15 | Token ceiling drops narrative before regulated content | T-RESIL | INJ-076 |
| AC-FR013-16 | Annotations labelled model-generated everywhere | T-UX | EU AI Act |
| AC-FR013-17 | Content-filter results stored for every call | T-BEHAV | governance |
| AC-FR013-18 | Groundedness eval: zero unsupported claims | T-METRIC | NFR-22 |
| AC-FR013-19 | Unset endpoint, deployment, version or region: zero calls, pack still delivered | T-GATE | AMB-14 |

## FR-014 — Evidence store, integrity and retention

| AC | Criterion (short) | Class | Fixture / inject |
|---|---|---|---|
| AC-FR014-01 | Complete chain per fixture run | T-BEHAV | all 15 |
| AC-FR014-02 | Tamper detected, first break reported | T-GATE | INJ-036 |
| AC-FR014-03 | Mid-chain deletion detected | T-GATE | INJ-029 |
| AC-FR014-04 | Unwritable store fails closed | T-RESIL | INJ-029 |
| AC-FR014-05 | Full model interaction stored in advisory mode | T-BEHAV | FR-013 |
| AC-FR014-06 | Zero secrets or identifiers in the store | T-SEC | INJ-062 |
| AC-FR014-07 | LLM logs expire at 90 days; expiry is an event | T-BEHAV | INJ-035 |
| AC-FR014-08 | Legal hold blocks expiry, refusal recorded | T-GATE | INJ-061 |
| AC-FR014-09 | Hold read live; zero cache keys | T-SEC | AP-9 |
| AC-FR014-10 | Clinical and ICSR records never expired | T-BEHAV | INJ-035 |
| AC-FR014-11 | One command returns the full chain | T-BEHAV | DoD §7 |
| AC-FR014-12 | Verifiable with vendors uninstalled | T-RESIL | INJ-083, 084 |
| AC-FR014-13 | Index rebuilt from the store reproduces exactly | T-RESIL | INJ-084 |
| AC-FR014-14 | Record layout identical across modes | T-METRIC | AP-12 |
| AC-FR014-15 | Cloud container immutability rejects overwrite | T-SEC | INJ-069 |
| AC-FR014-16 | One `outcome` record per request; closed nine; `abstained`/`denied` reconcile to `decisions` | T-BEHAV | INJ-077 |

## Coverage summary

**204 acceptance criteria across fourteen features.** Every one is machine-checkable — none says "appropriate", "reasonable" or "as needed". Every business rule maps to at least one AC, and no AC exists without a rule behind it.

Distribution by class is deliberate rather than incidental: `T-GATE` is the largest group, because most of what this system must do correctly is refuse.

Three features — FR-004, FR-008, FR-012 — have no public fixture. Their criteria are verified against team-derived scenarios built from `data/`, and the coverage record marks them team-derived so no one mistakes them for fixture-verified results.

Twenty-six criteria close the inject gap found by the audit in `traceability_gap_audit.md` §3, in two passes. The first sixteen — AC-FR001-13, FR002-14, FR003-12/13, FR004-11…16, FR005-17/18, FR009-14 and FR010-12/13/14 — answered injects named by no rule at all. The next ten — AC-FR001-14/15, FR002-15/16, FR003-14/15, FR004-17/18, FR005-19 and FR009-15 — answered injects that had a rule whose only verifying criterion tested a different scenario; BR-027, for instance, concerned serialisation aggregation gaps but was mapped to the deny-list criterion. Building the gate is what surfaced the second set, which is the argument for building it. All twenty-six are team-derived, since none of the injects involved has a public fixture.
