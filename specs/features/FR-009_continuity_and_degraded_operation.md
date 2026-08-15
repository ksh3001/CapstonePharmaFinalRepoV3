# FR-009 — Continuity and degraded operation

**Question this file answers:** what the system does when the model, the region or the vendor is gone, and how it avoids becoming more dangerous while degraded.

| Field | Entry |
|---|---|
| Workflow | Shared — applies to A, B and C |
| Contract | `advisory_nonexecuting.schema.json` for PUB-10 |
| Fixtures | PUB-10 (reliability) |
| Injects | 015, 069, 079, 081, 082, 083, 084 |
| Principles | AP-1, AP-4, AP-6, AP-12 |
| Owner | Platform / SRE lead, with quality lead |
| Phase | 4 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

A platform owner asks what happens during an outage, or an outage occurs and a workflow request arrives anyway.

## 2. Preconditions

Endpoint status and continuity requirements are readable · each workflow's manual runbook exists · the kill switch is reachable independently of the inference path.

## 3. Happy path

1. Read endpoint availability and each workflow's declared outage tolerance.
2. Determine, per workflow, whether it may continue AI-assisted, must degrade, or must go manual **immediately**.
3. Where a fallback endpoint exists, evaluate whether it is a permissible substitute — validation state, capability, and region.
4. If it is not permissible, do not use it. Engage `ai_disabled` and the manual runbook.
5. Produce the pack deterministically, stating what is degraded and what it costs the reviewer.
6. On restoration, require reconciliation of work performed during the outage before AI-assisted processing resumes.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| A workflow's tolerance is `0` hours — `pv_intake` in PUB-10 | The manual path engages **immediately**. There is no grace period to interpret |
| A tolerance field is empty | Treated as **not specified**, never as zero and never as unlimited. The neighbouring field is read before concluding |
| A smaller fallback model is available | Availability is not permission. Substitution requires equivalent validation for the task; otherwise degrade to `ai_disabled` |
| Fallback sits in a different region from the primary | Residency is re-evaluated for the data the workflow requires; a residency failure blocks the fallback |
| Degradation would widen automation | Refused. The system may only degrade toward **more** human involvement, never less |
| Region-wide outage | All workflows degrade per their own tolerance; the pack states which are manual |
| Vendor exit or retirement | Evidence and audit trails remain readable without the vendor; the exit path is documented and rehearsed |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-071** | Every mandatory workflow has a documented manual path that produces the same regulated artefacts without inference | 082 |
| **BR-072** | Outage tolerance is read per workflow from evidence. An empty field is "not specified" and raises a gap; it is never defaulted to zero or to infinity | 079 |
| **BR-073** | Model substitution requires equivalent validation for the specific task. An available endpoint is not an authorised one, and a smaller model is not a quieter version of a larger one | 081 |
| **BR-074** | Degradation may only reduce automation. No degraded mode grants the system authority it lacks when healthy | 079, 082 |
| **BR-075** | The kill switch disables inference without disabling the product, and it does not depend on the inference path to work | 082 |
| **BR-076** | Work performed during an outage is reconciled before AI-assisted processing resumes | 082 |
| **BR-077** | Vendor exit is survivable: evidence, audit trail and packs remain readable and reproducible with no vendor dependency | 083 |
| **BR-078** | Retirement preserves evidence and audit trails for their full retention period, independent of the application's lifecycle | 084 |
| **BR-141** | Where a source system is isolated by a security incident or sits behind an OT segmentation boundary, data from it is **stale by declaration**: every fact carries its last-known-good timestamp and the isolation event, and the pack states that the system is unreachable rather than presenting its last value as current. Integrity of data written near the incident window is **unconfirmed** until verified against an independent record, and unconfirmed data is never cited as authority. The system never bridges a segmentation boundary, never proposes reconnection, restoration or payment, never declares an environment clean, and continues to serve the manual path under BR-071 for the affected workflows | 069 |
| **BR-137** | Where an assignment normally made by an unavailable system was made manually during an outage, the manual record is admitted as evidence with its own provenance — who assigned, when, under which authority and against which contingency procedure — and is marked as manually assigned for the life of the record. On recovery the manual and system records are **reconciled and both retained**; the system record does not overwrite the manual one, a disagreement between them is a contradiction, and a manual assignment with incomplete provenance produces a gap rather than an assumed-correct value. The system never reconstructs what an assignment would have been, and never performs the assignment itself | 015 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR009-01** | The PUB-10 pack validates against `advisory_nonexecuting.schema.json` with zero errors | Contract test |
| **AC-FR009-02** | With `primary_large` down, `pv_intake` — whose `max_ai_outage_hours` is `0` — is reported as requiring the manual path immediately, with no grace period | `T-RESIL`, PUB-10, INJ-079 |
| **AC-FR009-03** | `batch_review` and `supply_planning`, at 14 days tolerance, are reported as able to continue degraded, with the deadline stated | `T-BEHAV`, PUB-10 |
| **AC-FR009-04** | The empty `max_ai_outage_days` for `pv_intake` and the empty `max_ai_outage_hours` for the other two are each read as "not specified" and neither is treated as a number | `T-ONT`, PUB-10 |
| **AC-FR009-05** | `fallback_small` is **not** substituted for `primary_large` without evidence of equivalent validation; the pack states the missing validation rather than assuming the fallback is fine | `T-GATE`, PUB-10, INJ-081 |
| **AC-FR009-06** | The region difference between `EU-West` and `OnPrem-DE` triggers a residency evaluation, and its outcome appears in the pack | `T-BEHAV`, PUB-10, INJ-064 |
| **AC-FR009-07** | No degraded mode enables an action prohibited in the healthy system, verified by running the full prohibited-action suite with inference disabled | `T-GATE`, INJ-082 |
| **AC-FR009-08** | With `AEGIS_RUNTIME_MODE=ai_disabled`, all three mandatory workflows produce schema-valid packs | `T-RESIL`, NFR-12, INJ-082 |
| **AC-FR009-09** | The kill switch is provably independent: it works with every inference endpoint unreachable | `T-RESIL` |
| **AC-FR009-10** | The manual runbook required for each workflow exists and is referenced by the pack; a missing runbook is a gap | `T-ARTEFACT`, PUB-10 |
| **AC-FR009-11** | An outage-period reconciliation step is required before AI-assisted resumption, and skipping it is blocked | `T-BEHAV`, INJ-082 |
| **AC-FR009-12** | Evidence and audit artefacts are readable and packs reproducible with all vendor integrations removed | `T-RESIL`, INJ-083, INJ-084 |
| **AC-FR009-13** | Three consecutive runs byte-identical in every degraded mode | Determinism |
| **AC-FR009-14** | A manually made assignment recorded during a service outage appears in `evidence[]` with its assigning identity, time, authority and procedure reference and a manual-assignment marker; where the recovered system record differs, both are retained as a contradiction and neither is overwritten; a manual record missing any provenance element produces a gap and no assumed value | `T-RESIL`, INJ-015 |
| **AC-FR009-15** | With a source system marked isolated, every fact from it renders its last-known-good timestamp and the isolation event and none is presented as current; facts written inside the incident window render `integrity_unconfirmed` and are cited as authority nowhere; the pack contains no reconnection, restoration, payment or environment-clean statement, and the affected workflows report the manual path | `T-RESIL`, INJ-069 |

## 7. AI and human boundary

Continuity decisions are deterministic. No model decides whether a fallback is acceptable — that decision is exactly the one an unavailable or degraded model is least fit to make. Humans own the choice to invoke the manual path early.

## 8. Out of scope

Failing over infrastructure · provisioning endpoints · negotiating vendor terms · deciding to retire the system · executing the manual runbook.

## 9. Ambiguities

None blocking. PUB-10's `max_ai_outage_hours: "0"` for `pv_intake` is read literally as zero tolerance, and the pack states that reading explicitly so a reviewer can correct it.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../nfrs.md` NFR-03, NFR-12, NFR-17 · master plan §13 (operations), §21 (kill switch).
