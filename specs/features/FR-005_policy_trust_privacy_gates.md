# FR-005 — Policy, trust and privacy gates

**Question this file answers:** who is allowed to ask for what, right now, and what happens to personal data along the way.

| Field | Entry |
|---|---|
| Workflow | Shared — enforced on every request before any engine runs |
| Contract | `advisory_nonexecuting.schema.json` for PUB-09 and PUB-11; contributes `authorization{}` to all contracts |
| Fixtures | PUB-09 (security), PUB-11 (privacy) |
| Injects | 004, 006, 011, 017, 030, 031, 035, 041, 050, 059, 060, 061, 062, 063, 064, 066, 067, 068, 070 |
| Principles | AP-2, AP-4, AP-9 |
| Owner | Security lead and DPO role, with architecture lead |
| Phase | 2 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

Every request, from every entry point. The gate runs before the engines and again before emission — an entitlement can lapse mid-run.

## 2. Preconditions

`user`, `purpose` and `as_of` are supplied · entitlement sources are readable · consent, legal-hold and residency state are readable **live**, never from cache (AP-9).

## 3. Happy path

1. Resolve the user against the authoritative identity source, and resolve their role spelling to a canonical `role_id` through the exhaustive table in `../registers/roles_and_entitlements.md` §3. An unmapped spelling is an unresolved identity and denies.
2. Compare the authoritative state against any gateway or cache state; **disagreement resolves to the more restrictive** outcome.
3. Check purpose against the declared purpose register for the requested object.
4. Check role entitlement for the object class and for any sensitive segment within it, against the matrix in `../registers/roles_and_entitlements.md` §4.
5. Check residency and cross-border constraints for the data the purpose requires.
6. Check consent state and any withdrawal, at `as_of`.
7. Apply minimisation and per-purpose pseudonymisation to anything that proceeds.
8. Record the decision, its inputs and its timestamp in `authorization{}` and the audit trail.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| IAM says revoked, AI gateway says `active_cached` | **Deny.** The authoritative source wins, the cached entitlement is reported as a control failure, and the gap between `revoked_at` and `cached_until` is stated (PUB-09) |
| Shared or generic account performing an approval action | Flagged as an attribution failure — the action cannot be attributed to a person, so it cannot support a regulated decision |
| Same identity active from two devices at once | Reported as an anomaly, not silently accepted; it does not by itself deny |
| Deletion request against data under legal hold | **Restriction, not deletion.** Processing stops, the record is retained, the conflict and both obligations are documented (PUB-11) |
| Consent withdrawn for one purpose but not another | Withdrawal is honoured per purpose. Processing that already occurred under `cached_active` consent is reported as a control failure |
| Cross-border transfer with no lawful basis in evidence | Deny the transfer path and state the missing basis |
| Purpose not in the register for that object | Deny. An unregistered purpose is never inferred from the request text |
| Denial | Emits a **valid pack** with `authorization.decision = "deny"` and a reason — never an unstructured error |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-039** | Authorisation is evaluated at execution time against the authoritative source. Cached, inherited or previously granted entitlement never authorises | 067 |
| **BR-040** | Where two entitlement sources disagree, the most restrictive outcome applies and the disagreement is reported as a finding | 067 |
| **BR-041** | Purpose is checked as well as identity. A user entitled to an object for one purpose is not entitled to it for another | 060, 063 |
| **BR-042** | A denial is a successful, schema-valid response. Denials are never exceptions and never leak the content that was withheld | 006, 068 |
| **BR-043** | A deletion request that collides with a legal hold or a retention obligation produces **restriction plus documentation**, never deletion and never refusal-without-explanation | 035, 061 |
| **BR-044** | Consent is evaluated per purpose at `as_of`; a withdrawal is effective from its own effective time, and prior processing under cached consent is reported | 017, 060 |
| **BR-045** | Residency and cross-border constraints are evaluated for the data the purpose requires, including any inference endpoint that would receive it | 064 |
| **BR-046** | Sensitive segments are role-gated against the entitlement matrix in `../registers/roles_and_entitlements.md` §4 and are **absent** from the pack for unentitled roles — not present-and-redacted, where their presence would itself disclose. An access group absent from the matrix is unentitled for every role; entitlement is never inferred from a role's seniority, its entitlement to a sibling group, or the absence of a prohibition | 041, 063 |
| **BR-047** | Re-identification risk from combining permitted fields is assessed, and a combination that defeats pseudonymisation is refused | 059, 062 |
| **BR-048** | Shared, generic or unattributable accounts cannot support an action that requires attribution; this is reported as a finding | 030 |
| **BR-048a** | A tool or model is callable only from a signed, approved manifest verified at execution time. An unsigned, altered or unlisted tool is refused, and the refusal is reported | 066, 070 |
| **BR-135** | Commercial or time pressure is not an input to any gate. Deadlines, revenue exposure, patent expiry, inspection dates and stated urgency do not appear in any decision path, and any field expressing them is excluded from gate evaluation by construction. A request marked urgent produces the same authorisation outcome, the same abstentions and the same evidence standard as the identical request unmarked. Urgency may change **priority**; it never changes the answer | 004, 050 |
| **BR-136** | A model or analytical tool is usable only for a purpose within its documented intended use, validated for that purpose and effective at `as_of`. Research-only, exploratory and unqualified models are refused for any GxP or regulatory purpose, and the refusal names the missing qualification. Availability is not authorisation, prior use elsewhere is not qualification, and a model is never promoted to a new purpose because it performed well on an old one | 011, 031 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR005-01** | PUB-09 and PUB-11 packs validate against `advisory_nonexecuting.schema.json` with zero errors | Contract test |
| **AC-FR005-02** | For `contractor_77`, whose IAM state is `revoked` while the gateway state is `active_cached` and `cached_until` is later than `as_of`, the decision is `deny`, and the pack cites both `users_entitlements.csv` and `access_cache.csv` | `T-GATE`, PUB-09, INJ-067 |
| **AC-FR005-03** | The revoked-but-cached condition produces a finding naming the window between `revoked_at` and `cached_until` | `T-BEHAV`, PUB-09 |
| **AC-FR005-04** | A denied request still returns a schema-valid pack with `execution_status: "not_executed"`, and no withheld content appears in it | `T-GATE`, INJ-006 |
| **AC-FR005-05** | Removing the entitlement cache from the inputs entirely does not change the decision for `contractor_77` — proving the cache is not load-bearing for allow | `T-GATE` |
| **AC-FR005-06** | For DSR-17 against subject `S-301-044` under active hold `LH-44`, the outcome is restriction with both obligations documented, and no field states that data was or will be deleted | `T-GATE`, PUB-11, INJ-061 |
| **AC-FR005-07** | Consent `C-044`, withdrawn for the biomarker purpose, blocks biomarker processing while leaving trial-purpose processing available, and processing event `PE-9` with `consent_check: cached_active` is reported as a control failure | `T-BEHAV`, PUB-11, INJ-017 |
| **AC-FR005-08** | The retention rule permitting deletion of AI prompt logs after 90 days is applied only where no evidence hold exists, and the hold check is shown | `T-BEHAV`, PUB-11 |
| **AC-FR005-09** | A request whose purpose is absent from the register is denied, with the unregistered purpose named | `T-GATE`, INJ-063 |
| **AC-FR005-10** | A cross-border path lacking a lawful basis is denied, including where the recipient is an inference endpoint in another region | `T-GATE`, INJ-064 |
| **AC-FR005-11** | For a role without sensitive-segment entitlement, the segment keys are **absent** from the serialised pack, verified by string search rather than by field inspection | `T-GATE`, INJ-063 |
| **AC-FR005-12** | Authorisation, consent, residency and hold state produce **zero cache keys** in any namespace, verified by inspecting the cache after a full run | `T-SEC`, AP-9 |
| **AC-FR005-13** | The `approve_sequence` action recorded against `lab_shared_night` is flagged as unattributable and cannot support a regulated decision; `site_coordinator_14`'s two-device login is reported as an anomaly without, by itself, denying | `T-BEHAV`, PUB-09, INJ-030 |
| **AC-FR005-14** | An unsigned, altered or unlisted tool manifest causes the tool call to be refused, and the refusal appears as a finding | `T-SEC`, INJ-066, INJ-070 |
| **AC-FR005-15** | A request that would move safety data outside its permitted boundary is denied, and no withheld content appears in the denial pack | `T-SEC`, INJ-068 |
| **AC-FR005-16** | Three consecutive runs byte-identical; `ai_disabled` produces the same decisions, since no decision here depends on a model | Determinism, `T-RESIL` |
| **AC-FR005-17** | For every gate-bearing fixture, a run with urgency, deadline and commercial-exposure fields populated at their most extreme values produces a pack **byte-identical** to the run with those fields absent, excluding only fields that record priority | `T-GATE`, INJ-004, INJ-050 |
| **AC-FR005-18** | A model or tool whose documented intended use does not cover the requested purpose is refused, the refusal names the missing qualification, and no output derived from it appears in the pack; a validated-for-another-purpose entry is refused on the same path as an unvalidated one | `T-GATE`, INJ-011, INJ-031 |
| **AC-FR005-19** | A combination of individually permitted genomic, demographic and temporal fields that narrows a cohort below the re-identification threshold is refused **as a combination**, the refusal states that a combination was withheld without naming the discriminating values, each field remains available where separately entitled, and the pseudonymisation mapping appears in no output | `T-GATE`, INJ-059 |

## 7. AI and human boundary

No model participates in an authorisation, consent, residency or hold decision — ever, in any mode. A model may summarise a decision already made, inside `human_review.annotations`. The kill switch does not affect this feature, which is the point: the gate cannot be turned off by disabling AI.

## 8. Out of scope

Granting, provisioning or revoking entitlements · performing deletions · filing DSR responses · changing consent records · approving cross-border transfers.

## 9. Ambiguities

None blocking. Re-identification assessment under BR-047 is rule-based over declared quasi-identifiers, not statistical; this is recorded as a limitation rather than presented as a risk score.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../data/state_transitions.md` §2 · `../api/api_contracts.md` · `../nfrs.md` NFR-09 · master plan §23 (data governance).
