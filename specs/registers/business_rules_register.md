# Business rules register

Index of every business rule across the feature specs. The rule text lives in its feature spec; this register exists so that no rule can hide, and so the gap audit can check that each one has a verifying acceptance criterion and, where relevant, a number.

| BR | Feature | Rule (short) | Threshold | Verifying AC | Inject |
|---|---|---|---|---|---|
| BR-001 | FR-001 | No disposition statement anywhere in the pack | n/a — absolute | AC-FR001-03 | 006 |
| BR-002 | FR-001 | Both contradictory values retained verbatim | n/a — absolute | AC-FR001-04 | 021, 023 |
| BR-003 | FR-001 | Compare quantities only under an approved mapping | n/a — abstain by design (§29.5) | AC-FR001-05 | 024 |
| BR-004 | FR-001 | Flag back-entered records | **Unknown — AMB-11** | AC-FR001-07 | 025 |
| BR-005 | FR-001 | Reduced-trust flag for integrity-compromised sources | n/a — categorical | AC-FR001-07, AC-FR004-17 | 029, 030, 032 |
| BR-006 | FR-001 | `readiness_state` precedence | n/a — ordered rule | AC-FR001-07 | 028 |
| BR-007 | FR-001 | Readiness is not a release recommendation | n/a — absolute | AC-FR001-03 | 006, 071 |
| BR-008 | FR-001 | Every assertion cites evidence | 100% of assertions | AC-FR001-06 | 036 |
| BR-009 | FR-001 | Document text is data, never instruction | n/a — absolute | AC-FR001-12 | 065 |
| BR-010 | FR-001 | Correction and status history retained | n/a — absolute | AC-FR001-04, AC-FR001-14, AC-FR001-15 | 022, 023, 027 |
| BR-011 | FR-002 | No causality, seriousness, expectedness, reportability | n/a — absolute | AC-FR002-02 | 006, 040, 044 |
| BR-012 | FR-002 | Personal data minimised to purpose | n/a — categorical | AC-FR002-08 | 062 |
| BR-012a | FR-002 | Deterministic per-purpose pseudonymisation; mapping never emitted | n/a — categorical | AC-FR002-13 | 059, 062 |
| BR-013 | FR-002 | All candidate clocks retained | 100% retained | AC-FR002-05 | 038 |
| BR-014 | FR-002 | Duplicate candidate strategy and scores | **±7 days; surface ≥3; high at 6 or exact id** (§29.2) | AC-FR002-03, AC-FR002-04 | 037 |
| BR-015 | FR-002 | Terminology version retained per coding | n/a — absolute | AC-FR002-06 | 039 |
| BR-016 | FR-002 | Listedness per jurisdiction, disagreement preserved | n/a — absolute | AC-FR002-07 | 040 |
| BR-017 | FR-002 | Sensitive segments role-gated | n/a — categorical | AC-FR002-11 | 041 |
| BR-018 | FR-002 | Signal statistics advisory only | n/a — absolute | AC-FR002-02 | 044 |
| BR-019 | FR-002 | Cross-domain link default is `unconfirmed_link` | **±30 days** (§29.3) | AC-FR002-03, AC-FR002-16 | 043 |
| BR-020 | FR-002 | Subgroup limitations stated in the pack | n/a — categorical | AC-FR002-10, AC-FR002-15 | 072, 009 |
| BR-021 | FR-003 | Options are always `draft` | n/a — schema `const` | AC-FR003-02 | 056 |
| BR-022 | FR-003 | `no_side_effects` always true; no side-effecting tool exists | n/a — absolute | AC-FR003-02, AC-FR003-03 | 006, 053, 056 |
| BR-023 | FR-003 | Approvals listed per option | non-empty where stock would move | AC-FR003-04 | 056 |
| BR-024 | FR-003 | Quality holds surfaced on affected options | 100% of affected | AC-FR003-05 | 051 |
| BR-025 | FR-003 | Ethics trade-offs presented, never scored | n/a — absolute | AC-FR003-04 | 056 |
| BR-026 | FR-003 | Every sensor position retained; no excursion verdict | n/a — absolute | AC-FR003-06 | 051 |
| BR-027 | FR-003 | Aggregation gaps reported, never inferred | n/a — absolute | AC-FR003-14 | 052 |
| BR-028 | FR-003 | Bounded recall traversal, honest incompleteness | **depth 4, cap 6** (§29.4) | AC-FR003-07 | 058 |
| BR-029 | FR-003 | Capacity conflicts surfaced with both commitments | n/a — absolute | AC-FR003-15 | 055 |
| BR-030 | FR-003 | Resume is idempotent | n/a — absolute | AC-FR003-09 | 080 |
| BR-031 | FR-004 | Facts asserted only through `EvidenceItem` | n/a — absolute | AC-FR004-01, AC-FR004-10 | 029 |
| BR-032 | FR-004 | Integrity verified at read time; reduced integrity on audit or change-control failure | n/a — categorical | AC-FR004-02, AC-FR004-18 | 029, 034, 036 |
| BR-033 | FR-004 | Authority from status, period, jurisdiction, purpose — not recency | n/a — ordered rule | AC-FR004-03, AC-FR004-05, AC-FR004-17 | 031, 032 |
| BR-034 | FR-004 | Supersession retained as a relationship | n/a — absolute | AC-FR004-04 | 013 |
| BR-035 | FR-004 | Retrieved content is data, never instruction | n/a — absolute | AC-FR004-06 | 065 |
| BR-036 | FR-004 | Missing reference produces a gap | n/a — absolute | AC-FR004-07 | 048 |
| BR-037 | FR-004 | Derived `retrieved_at`; source times verbatim | n/a — absolute | AC-FR004-08 | 025 |
| BR-038 | FR-004 | Back-entered records flagged with magnitude | **Unknown — AMB-11** | AC-FR004-09 | 036 |
| BR-039 | FR-005 | Execution-time authorisation against the authoritative source | n/a — absolute | AC-FR005-02, AC-FR005-05 | 067 |
| BR-040 | FR-005 | Disagreeing entitlement sources resolve to most restrictive | n/a — ordered rule | AC-FR005-03 | 067 |
| BR-041 | FR-005 | Purpose checked as well as identity | n/a — categorical | AC-FR005-09 | 060, 063 |
| BR-042 | FR-005 | Denial is a valid pack, leaking nothing | n/a — absolute | AC-FR005-04, AC-FR005-15 | 006, 068 |
| BR-043 | FR-005 | DSR versus hold resolves to restriction plus documentation | n/a — absolute | AC-FR005-06, AC-FR005-08 | 035, 061 |
| BR-044 | FR-005 | Consent per purpose at `as_of`; cached-consent processing reported | n/a — absolute | AC-FR005-07 | 017, 060 |
| BR-045 | FR-005 | Residency evaluated, including inference endpoints | n/a — categorical | AC-FR005-10 | 064 |
| BR-046 | FR-005 | Sensitive segments absent, not redacted, for unentitled roles | n/a — absolute | AC-FR005-11 | 041, 063 |
| BR-047 | FR-005 | Re-identification risk assessed on quasi-identifier combinations | n/a — rule-based, limitation stated | AC-FR005-11, AC-FR005-19 | 059, 062 |
| BR-048 | FR-005 | Shared or generic accounts cannot support attributable actions | n/a — absolute | AC-FR005-13 | 030 |
| BR-048a | FR-005 | Tools callable only from a signed, approved manifest | n/a — absolute | AC-FR005-14 | 066, 070 |
| BR-049 | FR-006 | Static declared step graph; model never chooses a step | n/a — absolute | AC-FR006-08 | 065 |
| BR-050 | FR-006 | Budgets declared before start | **50 000 tokens/request; ceilings in config** | AC-FR006-07 | 076 |
| BR-051 | FR-006 | Sync checkpoint before each step; no personal data | n/a — absolute | AC-FR006-06 | 080 |
| BR-052 | FR-006 | Resume requires freshness and hash match | **configured bound; PUB-13's 380 min exceeds it** | AC-FR006-02, AC-FR006-05 | 080 |
| BR-053 | FR-006 | Resume is idempotent under the request key | n/a — absolute | AC-FR006-03 | 080 |
| BR-054 | FR-006 | Execution-suggestive names grant no power | n/a — absolute | AC-FR006-04 | 006, 056 |
| BR-055 | FR-006 | Termination is always safe | n/a — absolute | AC-FR006-07, AC-FR006-09 | 076, 079 |
| BR-056 | FR-006 | Runner and model parity, byte-identical | 100% byte parity | AC-FR006-10 | 081, 082 |
| BR-057 | FR-007 | Cost per successful task, never per request | n/a — absolute | AC-FR007-03 | 077 |
| BR-058 | FR-007 | A zero cost is missing unless the source says nil | n/a — absolute | AC-FR007-04 | 077 |
| BR-059 | FR-007 | Review cost requires rate **and** duration, else abstain | n/a — abstain by design | AC-FR007-05 | 077, 078 |
| BR-060 | FR-007 | TCO includes inference, review, observability, platform | n/a — completeness rule | AC-FR007-04 | 077 |
| BR-061 | FR-007 | Price changes reported with both values; no restatement | n/a — absolute | AC-FR007-06 | 075 |
| BR-062 | FR-007 | Budgets enforced; exhaustion stops safely | **NFR-07, NFR-08 ceilings** | AC-FR007-08, AC-FR007-09 | 076 |
| BR-063 | FR-007 | Avoided inference measured and reported | n/a — measured | AC-FR007-10 | 077 |
| BR-063a | FR-007 | Vendor concentration reported with exit cost | n/a — categorical | AC-FR007-10a | 078 |
| BR-064 | FR-008 | No business rule in the console | n/a — absolute | AC-FR008-01 | AP-10 |
| BR-065 | FR-008 | Acknowledgement blocked until critical evidence opened | 100% of critical items | AC-FR008-02 | 071 |
| BR-066 | FR-008 | Acknowledgement labelled not-a-signature | n/a — absolute | AC-FR008-03 | 071 |
| BR-067 | FR-008 | Abstentions and gaps at equal prominence, never collapsed | n/a — absolute | AC-FR008-04 | 071 |
| BR-068 | FR-008 | No regulated-action control exists | zero controls | AC-FR008-01 | 006 |
| BR-069 | FR-008 | Unentitled content absent from the payload | n/a — absolute | AC-FR008-05 | 063 |
| BR-070 | FR-008 | WCAG 2.2 AA, keyboard operable, script-independent quality | **0 critical/serious axe findings** | AC-FR008-07, AC-FR008-08, AC-FR008-09 | 072, 073 |
| BR-070a | FR-008 | Segregation of duties enforced server-side | n/a — absolute | AC-FR008-12 | 074 |
| BR-071 | FR-009 | Documented manual path per mandatory workflow | 3 of 3 workflows | AC-FR009-08, AC-FR009-10 | 082 |
| BR-072 | FR-009 | Empty tolerance is "not specified", never zero or infinite | n/a — absolute | AC-FR009-04 | 079 |
| BR-073 | FR-009 | Substitution requires equivalent validation | n/a — categorical | AC-FR009-05 | 081 |
| BR-074 | FR-009 | Degradation only reduces automation | n/a — absolute | AC-FR009-07 | 079, 082 |
| BR-075 | FR-009 | Kill switch independent of the inference path | n/a — absolute | AC-FR009-09 | 082 |
| BR-076 | FR-009 | Outage work reconciled before AI resumption | n/a — absolute | AC-FR009-11 | 082 |
| BR-077 | FR-009 | Vendor exit survivable | n/a — absolute | AC-FR009-12 | 083 |
| BR-078 | FR-009 | Retirement preserves evidence for its retention period | n/a — absolute | AC-FR009-12 | 084 |
| BR-079 | FR-010 | Applicability by site approval, not recency | n/a — ordered rule | AC-FR010-02 | 013 |
| BR-080 | FR-010 | Global and local versions both preserved | n/a — absolute | AC-FR010-02, AC-FR010-03 | 013 |
| BR-081 | FR-010 | No eligibility, screen-failure or deviation statement | n/a — absolute | AC-FR010-06 | 014 |
| BR-082 | FR-010 | Every reference range presented with its origin | 100% of supplied ranges | AC-FR010-05, AC-FR010-07 | 014 |
| BR-083 | FR-010 | Obsolete-but-cached versions reported as risk | n/a — absolute | AC-FR010-03 | 013 |
| BR-084 | FR-010 | Consent evaluated per purpose before presenting subject data | n/a — categorical | AC-FR010-08 | 017 |
| BR-085 | FR-010 | Device timestamps preserved; skew reported, never corrected | n/a — absolute | AC-FR010-09 | 018 |
| BR-086 | FR-011 | Contract version travels with the fact | 100% of records | AC-FR011-05, AC-FR011-09 | 045 |
| BR-087 | FR-011 | Conversion only under an approved effective mapping | n/a — abstain by design | AC-FR011-02, AC-FR011-04 | 024 |
| BR-088 | FR-011 | No unapproved converted value is ever emitted | zero occurrences | AC-FR011-03 | 024 |
| BR-089 | FR-011 | Coding systems validated; failures reported, not repaired | n/a — absolute | AC-FR011-08 | 024 |
| BR-090 | FR-011 | Status values per version; no asserted equivalence | n/a — absolute | AC-FR011-07 | 023 |
| BR-091 | FR-011 | Date semantics and variable precision preserved | n/a — absolute | AC-FR011-10 | 025 |
| BR-092 | FR-012 | Identity conflicts surfaced; no master record synthesised | n/a — absolute | AC-FR012-02 | 045 |
| BR-093 | FR-012 | Labelling per market with version and approval state | n/a — absolute | AC-FR012-03 | 046 |
| BR-094 | FR-012 | All candidate commitment deadlines retained with basis | n/a — absolute | AC-FR012-04 | 047 |
| BR-095 | FR-012 | Sequence gaps reported, never renumbered | n/a — absolute | AC-FR012-05 | 048 |
| BR-096 | FR-012 | Variation classification never asserted | n/a — absolute | AC-FR012-06 | 049 |
| BR-097 | FR-012 | Urgency is not an input to any rule | byte-identical under urgency | AC-FR012-07 | 050 |
| BR-098 | FR-012 | No submission, approval or commitment-met assertion | n/a — absolute | AC-FR012-08 | 047, 048 |

| BR-099 | FR-013 | Model reads the finished pack only; no retrieval tool | n/a — absolute | AC-FR013-07 | 065 |
| BR-100 | FR-013 | Output reaches only `human_review.annotations` | n/a — absolute | AC-FR013-01 | 006 |
| BR-101 | FR-013 | Removing the model changes no regulated field | 100% byte parity | AC-FR013-01, AC-FR013-02 | 082 |
| BR-102 | FR-013 | Numeric closure: no number absent from the pack | zero tolerance | AC-FR013-03 | 024, 065 |
| BR-103 | FR-013 | Citation closure: every reference resolves in the pack | zero tolerance | AC-FR013-04 | 065 |
| BR-104 | FR-013 | Deny-list applies to generated text | zero occurrences | AC-FR013-05 | 006 |
| BR-105 | FR-013 | Advice labelled model-generated everywhere | n/a — absolute | AC-FR013-16 | EU AI Act |
| BR-106 | FR-013 | Pseudonymise and minimise before the prompt is built | n/a — absolute | AC-FR013-08 | 062 |
| BR-107 | FR-013 | Residency checked before the call | n/a — categorical | AC-FR013-09 | 064 |
| BR-108 | FR-013 | Entra managed identity; no key anywhere | n/a — absolute | AC-FR013-10 | 070 |
| BR-109 | FR-013 | Deployment and model version pinned and recorded | n/a — absolute | AC-FR013-11, AC-FR013-12 | 081 |
| BR-110 | FR-013 | Record-and-replay cassettes; tests never call live | zero live calls | AC-FR013-13 | 082 |
| BR-111 | FR-013 | Prompt templates versioned and change-controlled | n/a — absolute | AC-FR013-11 | 081 |
| BR-112 | FR-013 | Budgets bind; narrative is cut first | NFR-07, NFR-08 | AC-FR013-15 | 076 |
| BR-113 | FR-013 | Azure disclosed as single-vendor dependency | n/a — categorical | AC-FR007-10a | 078 |
| BR-114 | FR-014 | Append-only, content-addressed store | n/a — absolute | AC-FR014-02 | 036 |
| BR-115 | FR-014 | Hash chain makes alteration detectable | 100% detection | AC-FR014-02, AC-FR014-03 | 029, 036 |
| BR-116 | FR-014 | No evidence, no request | n/a — fail closed | AC-FR014-04 | 029 |
| BR-117 | FR-014 | Identical record set across modes | n/a — absolute | AC-FR014-14 | 084 |
| BR-118 | FR-014 | No database is the system of record | n/a — absolute | AC-FR014-13 | 084 |
| BR-119 | FR-014 | LLM logs expire at 90 days unless held | **90 days** (`retention_rules.csv`) | AC-FR014-07 | 035, 062 |
| BR-120 | FR-014 | Clinical and ICSR records never expired here | n/a — absolute | AC-FR014-10 | 035 |
| BR-121 | FR-014 | Hold read live at expiry, never cached | n/a — absolute | AC-FR014-08, AC-FR014-09 | 061 |
| BR-122 | FR-014 | Expiry is itself a chain event | n/a — absolute | AC-FR014-07 | 035 |
| BR-123 | FR-014 | Verifiable with all vendors removed | n/a — absolute | AC-FR014-12 | 083, 084 |
| BR-124 | FR-014 | No secret or direct identifier written | zero occurrences | AC-FR014-06 | 062 |
| BR-125 | FR-001 | Cleaning-validation campaign boundary presented; beyond-boundary raises a gap | n/a — absolute | AC-FR001-13 | 026 |
| BR-126 | FR-002 | Report validity criteria marked present/absent/**unverifiable**; no auto-submit or discard | n/a — categorical | AC-FR002-14 | 042 |
| BR-127 | FR-003 | Substitute qualification status stated; unqualified never counted as supply | n/a — absolute | AC-FR003-12 | 054 |
| BR-128 | FR-003 | Documentation mismatch reported field by field; no compliance assertion | n/a — absolute | AC-FR003-13 | 057 |
| BR-129 | FR-004 | Identifiers scoped by issuing organisation; no cross-org merge | n/a — categorical | AC-FR004-11 | 005 |
| BR-130 | FR-004 | Method version part of a measurement; no cross-method trend without an approved assessment | n/a — absolute | AC-FR004-12 | 007 |
| BR-131 | FR-004 | Local code resolved only within its issuing scope; collisions retained | n/a — categorical | AC-FR004-13 | 008 |
| BR-132 | FR-004 | Manipulation concern escalated, never cleared | n/a — absolute | AC-FR004-14 | 010 |
| BR-133 | FR-004 | Conflicting sources retained; licence scope honoured | n/a — absolute | AC-FR004-15 | 012 |
| BR-134 | FR-004 | Recurrence linked across taxonomy versions; no effectiveness verdict, no auto-close | n/a — absolute | AC-FR004-16 | 033 |
| BR-135 | FR-005 | Urgency is not an input to any gate; identical answer under pressure | n/a — absolute | AC-FR005-17 | 004, 050 |
| BR-136 | FR-005 | Model usable only within documented intended use, validated for that purpose | n/a — absolute | AC-FR005-18 | 011, 031 |
| BR-137 | FR-009 | Manual assignment during outage carries provenance; reconciled, never overwritten | n/a — absolute | AC-FR009-14 | 015 |
| BR-138 | FR-010 | Allocation absent for every role; inferential unblinding detected and withheld | n/a — absolute | AC-FR010-12 | 016 |
| BR-139 | FR-010 | Pending adjudication reported as pending; never counted, never predicted | n/a — absolute | AC-FR010-13 | 019 |
| BR-140 | FR-010 | Site risk as observations with evidence; no score, ranking or inspection call | n/a — absolute | AC-FR010-14 | 020 |
| BR-141 | FR-009 | Isolated system stale by declaration; incident-window writes unconfirmed; no boundary bridged | n/a — absolute | AC-FR009-15 | 069 |
| BR-142 | FR-014 | One `outcome` record per request, disposition from a closed nine; deliberate separated from failure; unclassifiable is `internal_error` | n/a — closed enumeration | AC-FR014-16 | 036, 077 |

## Gap audit

| Check | Result |
|---|---|
| Total rules | 146 across fourteen features |
| Rule with no verifying AC | None |
| Rule requiring a number but lacking one | BR-004 and BR-038 — the same back-entry materiality question, declared Unknown as AMB-11, owner GxP lead |
| AC with no rule | None |
| Rule with no inject, fixture or principle anchor | None |
| Inject cited that does not exist in `data/injects.json` | None — every ID verified against the source file |
| Inject with no rule behind it | None of the 81 behavioural injects. Injects 001, 002 and 003 are artefact obligations carried by `../testing/ac_test_plan.md` rather than by a rule |

Two rules share AMB-11 because they are the same decision seen from two features: FR-001 flags back-entry in a batch context, FR-004 flags it at the point the evidence is created. One human answer closes both.

**BR-125 to BR-140** were added after an automated audit found nineteen injects with a dimension owner and a plan §15 row but no rule and no criterion. Sixteen were behavioural gaps inside features that already existed; three were artefact obligations. The audit is recorded in `traceability_gap_audit.md` §3.
