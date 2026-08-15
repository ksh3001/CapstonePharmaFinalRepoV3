# FR-006 — Agent orchestration and human-in-the-loop

**Question this file answers:** how work is sequenced, bounded, paused for a human and resumed without doing anything twice.

| Field | Entry |
|---|---|
| Workflow | Shared — the runner beneath A, B and C |
| Contract | `advisory_nonexecuting.schema.json` for PUB-13; contributes `human_review{}` and `audit{}` to all contracts |
| Fixtures | PUB-13 (agent) |
| Injects | 006, 056, 065, 076, 079, 080, 081, 082 |
| Principles | AP-1, AP-2, AP-6, AP-12 |
| Owner | Architecture lead |
| Phase | 4 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

Invoked by every workflow request, and by a reviewer resuming an interrupted run.

## 2. Preconditions

The graph of steps for the workflow is declared statically · budgets are configured · `OrchestratorPort` resolves to the stdlib runner in `assessment` and to LangGraph in `ui`/`cloud` · any checkpoint being resumed exists and is readable.

## 3. Happy path

1. Admit the request and build the step graph for its workflow — a **fixed, declared** graph, not one the model chooses.
2. Persist a checkpoint before each step, synchronously.
3. Execute steps in declared order, decrementing step, token, time and tool budgets.
4. Where a human decision is required, `interrupt()` after checkpointing and emit an awaiting-review pack.
5. On resume, validate checkpoint freshness and the input hash, then continue from the recorded position.
6. Complete, package, audit, emit.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| Checkpoint older than the freshness bound | Refuse automatic resume; require explicit human confirmation and re-verify the underlying facts (PUB-13) |
| Checkpoint input hash no longer matches source | Same refusal, plus a finding that the world changed under the pause |
| Resume would re-emit work already produced | Idempotency key returns the original artefacts; **no second draft is created** |
| Step budget, token budget or wall-clock exhausted | Stop safely, checkpoint, emit a partial pack with a budget-stop abstention |
| A step fails repeatedly | Stop after the declared retry count; a loop is a failure, not a strategy |
| An unresolved high-risk contradiction is present | Stop and escalate rather than proceed to packaging |
| The model proposes a step outside the declared graph | Refused by the runner and recorded as an attempted excessive-agency event |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-049** | The step graph is static and declared in code. The model never chooses the next step, only produces content within a step. This is the excessive-agency control required by DoD §4 | 065 |
| **BR-050** | Every run declares maximum steps, elapsed time, input and output tokens, tool calls and cost before it starts. An undeclared budget is a refusal to start | 076 |
| **BR-051** | A checkpoint is written **before** each step with `durability="sync"`, and contains references, hashes and counters only — never personal data | 080 |
| **BR-052** | Resume requires a freshness check and an input-hash match. Stale or mismatched state requires human confirmation; silent resume does not exist | 080 |
| **BR-053** | Resume is idempotent under the request's idempotency key. Re-running produces the original artefacts and creates nothing new | 080 |
| **BR-054** | Any artefact carrying an execution-suggestive name — `draft_reservation` and its kin — remains a description with `status: "draft"` and no side effect. The name of a record never grants it power | 006, 056 |
| **BR-055** | Termination is always safe: checkpoint plus reason, never a partially applied regulated action | 076, 079 |
| **BR-056** | The LangGraph and stdlib runners produce byte-identical packs with inference disabled, and a model substitution must not change a pack. Parity failure blocks release | 081, 082 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR006-01** | The PUB-13 pack validates against `advisory_nonexecuting.schema.json` with zero errors | Contract test |
| **AC-FR006-02** | Run `AR-77` at checkpoint `cp-4` with `state_age_minutes: 380` is **not** resumed automatically; the pack states the staleness and requires human confirmation | `T-GATE`, PUB-13, INJ-080 |
| **AC-FR006-03** | Resuming `AR-77`, whose recorded `resume_result` is `duplicates_created`, produces **no third draft**: `DR-1` and `DR-2` are reported as pre-existing and the count is unchanged | `T-RESIL`, PUB-13 |
| **AC-FR006-04** | Both `DR-1` and `DR-2` are reported with `status: "draft"` and `no_side_effects: true`, and neither is described as a reservation that exists | `T-GATE`, INJ-056 |
| **AC-FR006-05** | A checkpoint whose input hash no longer matches source blocks resume and raises a finding | `T-GATE`, INJ-080 |
| **AC-FR006-06** | Checkpoint contents scanned across all fixtures contain zero personal-data fields | `T-SEC`, INJ-062 |
| **AC-FR006-07** | Exhausting the step budget mid-run emits a partial pack with a budget-stop abstention and a valid schema, not a truncated answer | `T-RESIL`, INJ-076 |
| **AC-FR006-08** | An injected instruction attempting to add a step outside the declared graph is refused and recorded; the pack is byte-identical to the clean run | `T-GATE`, INJ-065 |
| **AC-FR006-09** | The declared retry count is never exceeded, and a repeatedly failing step terminates rather than looping | `T-RESIL` |
| **AC-FR006-10** | LangGraph and stdlib runners produce byte-identical output on all 15 fixtures with inference disabled, and swapping the configured model changes no pack | `T-METRIC`, NFR-13, INJ-081 |
| **AC-FR006-11** | Three consecutive runs byte-identical; `ai_disabled` still completes every workflow | Determinism, `T-RESIL` |

## 7. AI and human boundary

AI may generate content **inside** a step. It may not choose steps, call tools that were not pre-bound to the step, extend a budget, resume a run, or decide that a contradiction is unimportant. Human confirmation is required to resume stale state and to close an interrupt.

## 8. Out of scope

Autonomous replanning · dynamic tool discovery at runtime · multi-agent negotiation · self-modifying graphs · any execution of a regulated action on resume.

## 9. Ambiguities

The checkpoint freshness bound is configured, not guessed: PUB-13's 380 minutes must exceed it. The default is recorded in `packages/config` and any change is an ADR.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../data/state_transitions.md` §3 · `../nfrs.md` NFR-07, NFR-13 · master plan §20 (orchestration), §32 (agent roster).
