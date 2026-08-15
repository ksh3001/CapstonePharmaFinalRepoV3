# FR-007 — FinOps budgets and cost reporting

**Question this file answers:** what does a successful task actually cost, and what stops a run from spending without limit.

| Field | Entry |
|---|---|
| Workflow | Shared — budgets enforced on every run; reporting is its own advisory task |
| Contract | `advisory_nonexecuting.schema.json` for PUB-14; contributes `metrics{}` to all contracts |
| Fixtures | PUB-14 (finops) |
| Injects | 075, 076, 077, 078 |
| Principles | AP-3, AP-4, AP-12 |
| Owner | FinOps / platform lead |
| Phase | 6 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

Two triggers. Enforcement runs on every request. Reporting runs when a platform owner asks for cost per successful task.

## 2. Preconditions

Usage, price, cost-model and staff-rate sources are readable and hash-verified · the definition of "successful task" is declared, not inferred · budget ceilings are configured.

## 3. Happy path

1. Load usage, prices, cost model and staff rates through FR-004.
2. Compute inference cost per workflow from tokens and the price effective at `as_of`.
3. Compute cost per **successful** task, using the declared success definition and the successful-task count — never the request count.
4. Add human review cost from measured review time and loaded rates.
5. Add platform and observability cost.
6. Report the total, its components, and every input that was missing.
7. Compare against ceilings and report headroom.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| A cost line is `0` where a cost certainly exists — `human_quality_review`, `medical_review` in PUB-14 | Treated as **missing, not zero.** A gap is raised and the total is reported as incomplete. A zero that is really an absence is the most expensive mistake in this feature |
| Review minutes per task are not in evidence | Total cost per successful task **abstains**. Loaded hourly rates without duration do not yield a cost, and multiplying by an assumed duration would fabricate the answer |
| Vendor price differs from the previously recorded price | Both prices reported with the change and its effect on unit economics; the newer price is not silently adopted for historical periods |
| Success definition unavailable or contested | Report cost per request and abstain on cost per successful task, naming the missing definition |
| Budget ceiling reached mid-run | Stop safely per FR-006 BR-055; a partial pack with a budget-stop abstention |
| Cumulative wallet ceiling reached | Refuse to start new runs and alert; no run is allowed to borrow against the ceiling |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-057** | Cost is reported **per successful task**, never per request. Requests that failed or abstained are the denominator's problem, not hidden from it | 077 |
| **BR-058** | A zero in a cost source is treated as missing unless the source explicitly states that the cost is nil. Absence of a number is never a number | 077 |
| **BR-059** | Human review cost requires both a rate and a duration. With only a rate, the system abstains rather than assumes | 077, 078 |
| **BR-060** | Total cost of ownership includes inference, human review, observability and platform. A partial total is labelled partial, with the missing components named | 077 |
| **BR-061** | Price changes are reported with both values and the effective dates. Historical spend is never restated at the new price | 075 |
| **BR-062** | Per-request and cumulative budgets are enforced in code, and exhaustion produces a safe stop rather than a truncated answer | 076 |
| **BR-063** | Avoided inference — work completed deterministically or served from cache — is measured and reported, so that efficiency claims are evidenced rather than asserted | 077 |
| **BR-063a** | Dependence on a single vendor is reported as a concentration risk with the exit cost stated, wherever cost is reported | 078 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR007-01** | The PUB-14 pack validates against `advisory_nonexecuting.schema.json` with zero errors | Contract test |
| **AC-FR007-02** | Inference cost per workflow is computed from tokens and prices, and recomputing by hand from `model_usage.csv` and `model_costs.csv` reproduces the figure exactly | `T-METRIC`, PUB-14 |
| **AC-FR007-03** | Cost per successful task uses `successful_tasks` as the denominator — 1110 for `batch_review`, 2800 for `pv_intake` — and never `requests` | `T-METRIC`, PUB-14, INJ-077 |
| **AC-FR007-04** | The `0` values for `human_quality_review` and `medical_review` produce gaps stating the cost is missing, and no total is presented as complete | `T-BEHAV`, PUB-14, INJ-077 |
| **AC-FR007-05** | Total cost per successful task **abstains** with reason `human_review_duration_unavailable`, because `staff_rates.csv` supplies rates but no evidence supplies review minutes | `T-BEHAV`, PUB-14 |
| **AC-FR007-06** | The `large-1` price change from `5.00` to `8.50` per million input tokens is reported with both values and its effect on unit cost | `T-BEHAV`, PUB-14, INJ-075 |
| **AC-FR007-07** | No pack presents an estimated, interpolated or assumed cost figure; every number traces to a source record | `T-GATE` |
| **AC-FR007-08** | Exceeding the per-request token ceiling stops the run and emits a budget-stop abstention rather than a shortened answer | `T-RESIL`, NFR-07, INJ-076 |
| **AC-FR007-09** | The cumulative wallet ceiling blocks new runs when reached, proven by a test that drives usage past the limit | `T-SEC`, NFR-08, INJ-076 |
| **AC-FR007-10** | Avoided-inference count and cache-hit rate are reported and are consistent with the run's actual model calls | `T-METRIC`, INJ-077 |
| **AC-FR007-10a** | Single-vendor concentration is reported wherever cost is reported, naming the exit cost and the alternative on record | `T-BEHAV`, INJ-078 |
| **AC-FR007-11** | All monetary arithmetic uses decimal with a declared rounding mode; no binary float reaches serialisation | `T-METRIC`, plan §28 |
| **AC-FR007-12** | Three consecutive runs byte-identical; `ai_disabled` still produces the cost report, since the report requires no inference | Determinism, `T-RESIL` |

## 7. AI and human boundary

No model computes, estimates or reconciles a cost figure. Arithmetic is deterministic code. A model may narrate a computed result inside `human_review.annotations`. Deciding what to do about the cost — renegotiate, switch model, reduce scope — is a human decision this feature never makes.

## 8. Out of scope

Changing model routing to save money · negotiating vendor pricing · setting budgets · approving spend · forecasting future cost.

## 9. Ambiguities

None blocking. The definition of "successful task" is taken from the source column `successful_tasks` and is recorded as a source-supplied definition rather than one the team invented — a distinction the pack states explicitly.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../nfrs.md` NFR-07, NFR-08 · master plan §24.4 (token economics), §28 (decimal handling).
