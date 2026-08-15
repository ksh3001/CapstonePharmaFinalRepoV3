# Spec ambiguities register

Every ambiguity is either **closed** with a decision, or **declared Unknown** with an owner and a trigger. Nothing is left implicit.

## Closed

| ID | Ambiguity | Decision | Where recorded |
|---|---|---|---|
| AMB-01 | Seven fixtures require an `advisory_nonexecuting` contract that the package does not ship | Team-authored schema from the shared invariant core; may add obligations, never relax one | Plan §27; `../api/advisory_nonexecuting.schema.json` |
| AMB-02 | What `integrity.sha256` hashes | The published source-artefact hash, cross-checked against `FILE_HASHES.csv`; never a recomputed row digest | Plan §27; `../api/api_contracts.md` §3 |
| AMB-03 | Origin of `retrieved_at`, `checked_at`, `request_id` | Derived from `as_of` and content hashes; the clock is never sampled | Plan §27, §28 |
| AMB-04 | Serialisation and array ordering | Canonical JSON with declared sort keys and tiebreakers | Plan §28 |
| AMB-06 | Cost per successful task offline | Two named bases, `reviewer_accepted` and `offline_proxy`, recorded per run | Plan §24.4 |
| AMB-07 | Parity scope with inference enabled | Parity claimed with inference off; otherwise excluding `human_review.annotations` | Plan §9.5, §27 |
| AMB-08 | Interpreter version | CPython ≥ 3.11, < 3.14 | Plan §4 rule 4a |
| AMB-09 | Fixture copy set | Derived from fixture `evidence_references`, re-derived in CI | Plan §3.2 |
| AMB-10 | Delivery cut line | Minimum defensible submission with an explicit drop order | Plan §30.4 |

## Declared Unknown — proceed with a default, surfaced as configuration

| ID | Unknown | Working default | Owner | Resolution trigger | Risk if wrong |
|---|---|---|---|---|---|
| **AMB-05a** | PV duplicate-candidate window and score cut points are a design choice, not a validated PV business rule | ±7-day onset window; surface at score ≥3; high at 6 or exact worldwide-unique-id | Safety physician role | Human-review panel (plan §25.6) or a PV SME review | Too tight hides real duplicates; too loose floods the reviewer. Either way it is a *candidate* list, so no case is merged incorrectly — the failure mode is reviewer workload, not data corruption |
| **AMB-05b** | Cross-domain linkage window for complaint ↔ batch ↔ ICSR | ±30 days, abstain as `unconfirmed_link` below the bar | Domain lead | Panel review | Missed association surfaces as a gap rather than a false link |
| **AMB-11** | Materiality threshold for flagging a back-entered record, where `recorded_at` differs from `event_time` | Flag **any** difference greater than zero, and report the magnitude | GxP / quality lead | Quality review of flag volume in Phase 1 | Flagging everything is noisy but safe; a threshold chosen without quality input could hide a real integrity signal |
| **AMB-14** | Azure endpoint, deployment name, model version and region — credentials to be supplied by the product owner | **No default.** Unset configuration is treated as a residency failure: zero outbound calls, missing setting named, pack still delivered | Product owner | Credentials supplied | None. Failing closed cannot send data anywhere unintended; the cost is that advice is absent until configured |
| **AMB-13** | Whether the Azure OpenAI deployment holds the Limited Access exemption from abuse monitoring. Without it, the provider retains prompts for human review — a processing decision, not a platform detail | Assume **no exemption**: send only pseudonymised, minimised content (BR-012a, BR-106) | DPO role | Confirmation from the Azure subscription owner, recorded in `compliance/eu-ai-act/` | If the exemption is wrongly assumed present, personal data sits in a provider's review queue outside the declared processing boundary. Assuming its absence is the safe direction and costs only prompt richness |
| **AMB-15** | Which roles are entitled to which sensitive-segment access group. `sensitive_segments.csv` supplies segment → access group and `users_entitlements.csv` supplies user → role, but the package contains **no role → access group edge**, so BR-046 had a gate with no table | `PV_PREGNANCY` and `PV_PAEDIATRIC` entitle `safety_physician` only, on clinical-necessity grounds; **every unlisted group is unentitled for every role**, including `auditor` | Security / privacy lead with the DPO role | A DPO-approved entitlement matrix, or the package supplying the edge | Fail-closed in the safe direction: a wrongly-denied segment is a visible gap the reviewer can escalate, whereas a wrongly-granted one is an undetected disclosure. The cost is that a legitimately entitled role may have to request access explicitly |
| **AMB-12** | Whether the human-review panel can run before the defence tag given participant availability | Assume one session; if it cannot run, L7 is reported as not executed rather than assumed passed | Evaluation lead | Phase 6 planning | Overstating reviewer validation — mitigated by explicit non-claim |

## Rules for this register

A default may ship only if it is: surfaced in configuration, visible in the output pack, and safe in the direction of abstention. A default that resolves a conflict, merges a record or asserts completeness is never acceptable — those abstain instead.

No open ambiguity currently blocks Phase 0 or Phase 1. AMB-05a and AMB-05b block **claiming validated PV matching behaviour**, not implementing it.
