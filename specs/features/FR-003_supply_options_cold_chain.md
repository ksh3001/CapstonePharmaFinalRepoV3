# FR-003 — Supply options and cold-chain recovery

**Question this file answers:** what must the system do when a supply governance user asks for options in response to a shortage or a cold-chain excursion.

| Field | Entry |
|---|---|
| Workflow | C — `supply_options` |
| Contract | `evaluation/contracts/supply_response.schema.json` |
| Fixtures | PUB-07, PUB-08 |
| Injects | 051, 052, 053, 054, 055, 056, 057, 058, 080 |
| Principles | AP-1, AP-2, AP-4, AP-7, AP-8 |
| Owner | Supply governance board role, with architecture lead |
| Phase | 3 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

A supply planner or governance board member requests options for a disruption event, by CLI or console, with `user`, `purpose`, `as_of` and the execution flag.

## 2. Preconditions

Authorisation returns `allow` · the event identifier resolves · quality-hold state is read live · source artefacts are hash-verified · checkpoint state, if resuming, passes the freshness check.

## 3. Happy path

1. Admit, authorise, apply budgets, validate any checkpoint being resumed.
2. Load event context: lanes, loggers, inventory positions, CMO capacity, customs documents, quality holds.
3. Project the bounded provenance graph for affected lots and shipments.
4. Reconcile disputes — logger against pallet sensor, aggregation gaps, capacity double-promises — retaining all positions.
5. Generate options, each with its constraints, dependencies and unresolved questions.
6. Attach the approval path and the quality holds that bind each option.
7. Assemble with `no_side_effects: true`, validate, audit, emit.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| A lot is under quality hold | The hold is attached to every option touching that lot; no option proposes bypassing it |
| Logger and pallet sensor disagree | Both readings retained; no excursion verdict is issued and no product status changes |
| Recall scope cannot be bounded within the traversal limit | `traversal_incomplete: true`, unexplored frontier listed, abstention raised — scope completeness never asserted |
| Counterfeit indicators present | A suspicion finding with indicators and escalation path; no recall initiation, no market action |
| Customs description and licence disagree | Reported as a constraint on the affected option |
| Checkpoint is stale or hash-mismatched | Refuse silent resume; require human confirmation and start a fresh interrupt |
| Budget exhausted mid-generation | Emit the options produced so far, marked partial, with a budget-stop abstention |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-021** | Every option has `status: "draft"`. No other status is representable | 056 |
| **BR-022** | `no_side_effects` is always `true`. The system holds no tool that can reserve, allocate, ship, release or recall | 006, 053, 056 |
| **BR-023** | Every option lists the approvals required before anyone may act on it | 056 |
| **BR-024** | Quality holds are surfaced on every option they affect, and no option is ranked in a way that implies overriding one | 051 |
| **BR-025** | Allocation ethics trade-offs are presented as explicit trade-offs with their affected populations, never resolved by a scoring function | 056 |
| **BR-026** | Cold-chain disputes retain every sensor position with its device, calibration state and time basis; no excursion conclusion is drawn | 051 |
| **BR-027** | Serialisation aggregation gaps are reported as gaps, not repaired or inferred | 052 |
| **BR-028** | Recall-scope traversal is bounded per master plan §29.4 and reports incompleteness honestly | 058 |
| **BR-029** | CMO capacity conflicts are surfaced with both commitments and their sources | 055 |
| **BR-030** | Resuming a run is idempotent: the same request produces the same pack and repeats no work | 080 |
| **BR-127** | Where a critical raw material or excipient is short, each option states the qualification status of every substitute it names — qualified, qualified for a different product or grade, or unqualified — together with the change-control and regulatory-variation steps that substitution would require. An unqualified substitute may be **described** but is never presented as available supply, and no option implies that a shortage justifies bypassing qualification | 054 |
| **BR-128** | Where shipping documentation disagrees with the licence, the export licence or the customs declaration — product description, quantity, classification or consignee — every position is retained with its document and issuing authority, and the mismatch is reported as a finding naming the fields that differ. The system never selects the correct description, never states that a shipment is compliant or clearable, and never proposes amending a document to resolve the mismatch | 057 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR003-01** | PUB-07 and PUB-08 packs validate against `supply_response.schema.json` with zero errors | Contract test |
| **AC-FR003-02** | Every element of `options[]` has `status: "draft"`, and `no_side_effects` is `true` | Contract test |
| **AC-FR003-03** | No pack contains an execution verb — reserve, allocate, ship, release, recall, dispose — in any string field | `T-GATE` deny-list |
| **AC-FR003-04** | `approvals_required[]` is non-empty for every option that would change physical stock if acted upon | `T-BEHAV`, INJ-056 |
| **AC-FR003-05** | A lot under quality hold appears in `quality_holds[]` and on every option referencing it | `T-BEHAV`, INJ-051 |
| **AC-FR003-06** | A logger-versus-pallet dispute yields a contradiction with both readings and no excursion verdict | `T-KG`, INJ-051 |
| **AC-FR003-07** | A recall-scope query exceeding the hop limit sets `traversal_incomplete: true`, lists the frontier, and raises an abstention | `T-KG`, INJ-058 |
| **AC-FR003-08** | Counterfeit indicators produce a suspicion finding and an escalation path, and no recall language | `T-GATE`, INJ-053 |
| **AC-FR003-09** | Replaying a completed request with the same idempotency key returns the original pack and performs no recomputation of side-effecting steps | `T-RESIL`, INJ-080 |
| **AC-FR003-10** | A stale or hash-mismatched checkpoint blocks automatic resume and requires human confirmation | `T-GATE`, INJ-080 |
| **AC-FR003-11** | Three consecutive runs byte-identical; `ai_disabled` still produces a valid pack | Determinism, `T-RESIL` |
| **AC-FR003-12** | An option naming an unqualified substitute carries its qualification status and the required change-control and variation steps, and appears in no available-supply total; a pack containing an unqualified substitute contains no statement that it may be used | `T-BEHAV`, INJ-054 |
| **AC-FR003-13** | A consignment whose declared description conflicts with its licence produces a finding naming each differing field, with every position retained and attributed to its issuing authority; the pack contains no compliance or clearance assertion and no proposed document amendment | `T-BEHAV`, INJ-057 |
| **AC-FR003-14** | A case with no aggregation record to its pallet produces a gap naming the case and the expected parent; the pack infers no parent from proximity, sequence or timing, and reports no aggregation hierarchy as complete where a gap exists | `T-KG`, INJ-052 |
| **AC-FR003-15** | Where a contract manufacturer's committed capacity is promised to more than one demand, every commitment appears with its source document and committed quantity, and the over-commitment is reported as a finding; no option treats the contested capacity as available, and the system allocates none of it | `T-BEHAV`, INJ-055 |

## 7. AI and human boundary

AI may, when enabled: generate option drafts and summarise constraints. It may not rank options by desirability, resolve an ethical trade-off, or assert that an option is safe. The set of options and their constraints is deterministic; model text, if present, is labelled annotation inside `human_review.annotations`.

## 8. Out of scope

Reservation, allocation, shipment, release, recall initiation, quality-status change, customs filing, contract commitment.

## 9. Ambiguities

The ±30-day linkage window (master plan §29.3) applies here for lot-to-event association and is a team-set default. No blocking ambiguity.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../api/api_contracts.md` · master plan §29.4 (traversal), §20.4 (checkpoints), §28 (determinism).
