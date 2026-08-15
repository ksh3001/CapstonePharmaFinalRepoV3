# API and response contracts

**Question this file answers:** exactly what shape must responses take, what is forbidden inside them, and how errors are expressed.

## 1. Contract set

| Contract | Source | Applies to |
|---|---|---|
| `batch_response.schema.json` | Challenge package — authoritative, immutable | PUB-01, 02, 03 |
| `pv_response.schema.json` | Challenge package — authoritative, immutable | PUB-04, 05, 06 |
| `supply_response.schema.json` | Challenge package — authoritative, immutable | PUB-07, 08 |
| `evidence_item.schema.json` | Challenge package — authoritative, immutable | Referenced by all of the above |
| `advisory_nonexecuting.schema.json` | **Team-authored** (AMB-01) | PUB-09, 10, 11, 12, 13, 14, 15 |

The four challenge schemas are copied unmodified and hash-verified. Editing one is a build failure.

## 2. Why the team contract exists

Seven of the fifteen fixtures declare `"response_contract": "advisory_nonexecuting"`, and the package ships no such schema. Rather than emit an unvalidated object for nearly half the evaluation set, the team authors one from the invariant core the three regulated schemas share:

```
request_id · workflow · as_of · authorization{user, purpose, checked_at, decision, reason?}
evidence[] · contradictions[] · gaps[] · abstentions[]
human_review · execution_status = "not_executed" · audit
```

To that core it adds `scenario_id`, a closed `workflow` enum, `findings[]`, `required_reviews[]`, `gate_outcome`, `no_side_effects: true` and an optional `metrics` object for FinOps. `additionalProperties` is `false` throughout.

**The enum is derived from the feature set, not the fixture set.** It holds **eight** values — `security`, `privacy`, `reliability`, `integration`, `agent`, `finops`, `clinical`, `regulatory`. The first seven correspond to the seven public advisory fixtures; `regulatory` exists because FR-012 declares this contract and has no public fixture. Building the enum from the fixtures was a real defect: FR-012 was authored later to adopt the orphaned D07 injects, no value was added, and because `workflow` is required under `additionalProperties: false`, that feature could not emit a valid pack at all — AC-FR012-01 was unsatisfiable. `tests/contract/test_contract_representability.py` now asserts that every feature declaring this contract has a value here, so the next feature added cannot repeat it.

**Standing rule:** the team contract may add obligations, never relax one. It carries `"description"` marking it as team-authored so no reader mistakes it for challenge evidence, and any pack it validates is also subject to the prohibited-field deny-list that applies to the regulated schemas.

## 3. Invariants that hold across every contract

| Invariant | Rule |
|---|---|
| Non-execution | `execution_status` is always `not_executed`; the advisory contract additionally requires `no_side_effects: true` |
| Closure | Every schema is `additionalProperties: false`. Nothing may be bolted on |
| Overflow | Traversal traces, agent step logs, budget records and model annotations do **not** belong in the response. They go to `evidence/` as separate artifacts (AP-7) |
| Citation | Every assertion cites at least one `evidence[]` entry by `record_id` |
| Provenance | Each evidence item carries `source`, `record_id`, `authority`, `effective_at`, `retrieved_at` and `integrity{sha256, source_preserved: true}` |
| Hash meaning | `integrity.sha256` is the **published source-artefact hash** (AMB-02), cross-checked against `FILE_HASHES.csv`. `audit.hash_scope` records `source_artifact` |
| Time | `retrieved_at` and `authorization.checked_at` derive from `authorized_context.as_of`, never the clock (AMB-03). Source timestamps are reproduced verbatim |
| Determinism | Canonical JSON per master plan §28 |

## 4. Prohibited content — deny-list

No string field, at any depth, may contain a disposition or execution statement. The deny-list is versioned in `packages/contracts/deny_list.json`, signed by its baseline hash, and may only grow — a shrink requires an approved exception record (master plan §23.3).

Categories: batch release or rejection · disposition setting · PV causality, seriousness, expectedness or reportability conclusions · clinical eligibility determinations · stock reservation, allocation or shipment · quality-status change · recall initiation · regulatory submission · approval or signature language.

The grader checks rendered strings, not just field names, because the risk is a sentence, not a key.

## 5. Error envelope

Errors never leave the API as a stack trace or a free-form message, and never carry evidence content.

```json
{
  "error": {
    "code": "AUTHZ_DENIED",
    "message": "Human-readable, no personal data, no source content",
    "request_id": "REQ-…",
    "as_of": "2026-08-01T08:00:00Z",
    "retryable": false
  }
}
```

Codes: `AUTHZ_DENIED` · `PURPOSE_NOT_COVERED` · `RESIDENCY_BLOCKED` · `INTEGRITY_FAILED` · `TOOL_UNTRUSTED` · `MODEL_UNVERIFIED` · `BUDGET_EXHAUSTED` · `CHECKPOINT_STALE` · `CONTRACT_INVALID` · `SOURCE_UNAVAILABLE`.

A denial is a normal outcome and is preferred over an error where the contract can express it: an authorisation refusal is emitted as a valid pack with `authorization.decision = "deny"`, not as an HTTP error, so it is auditable in the same form as any other result.

## 6. Module rules

Each rule names what enforces it. A rule enforced only by review is marked as such, because calling a convention a control is how boundaries erode.

| Rule | Statement | Enforced by |
|---|---|---|
| MR-1 | The UI never bypasses the API. No fetch reaches a data source directly (AP-10) | **Structural** — the console is server-rendered by `services/api`, so there is no client data path to misuse (plan §6, ADR-011) |
| MR-2 | No business rule exists in `apps/web`. The console renders packs and collects acknowledgements. Templates receive a validated pack and format it; a template that computes a value is a rule in the view | **Review**, plus the partial structural guarantee that gating decisions are re-evaluated server-side (§7) so a template cannot grant what the server withheld |
| MR-3 | The API validates every response against its contract **before** it leaves the service; an invalid pack is an internal error, never a partial send | Contract tests (TASK-004) |
| MR-4 | `packages/` never imports an adapter or a third-party package (master plan §4 rule 5) | **Gate** — stdlib import gate, TASK-001 step 5 |
| MR-5 | Only `packages/domain` may decide what a contradiction, gap or abstention is. The orchestrator sequences; it does not classify | **Gate** — module boundary gate, TASK-001 step 9: literal construction of `Contradiction`, `Gap` or `Abstention` outside `packages/domain` fails the build |
| MR-6 | Only `packages/kernel` writes the audit trail | **Gate** — module boundary gate: an audit-writer call outside `packages/kernel` fails the build |
| MR-7 | Imports inside `packages/` run downward through the tiers in master plan §4a, and the core import graph is acyclic. `packages/test-support` is importable only from `tests/` | **Gate** — module boundary gate: layering, cycle and test-isolation checks |

MR-5 and MR-7 were review-only until v3.8. MR-5 is the rule that keeps classification out of orchestrator nodes, which is the whole basis of the determinism claim, and risk R-10 predicts exactly that erosion — so leaving its defence to a design review was the weakest link in the module structure.

## 7. HTTP surface (advisory, ui and cloud modes; absent in assessment)

**JSON API.** `GET /api/workflows/batch/{batch_id}` · `GET /api/workflows/pv/{case_set_id}` · `GET /api/workflows/supply/{event_id}` · `GET /api/scenarios/{scenario_id}` (advisory contract) · `GET /api/evidence/{record_id}` · `GET /api/gates` · `GET /api/injects/coverage`.

**Mutations — the complete set, two of them.** `POST /api/reviews/{request_id}/acknowledge` and `POST /api/reviews/{request_id}/contest`. Both record a human workflow event and **neither is a signature** (master plan §11).

**Console.** The routes in master plan §6.2 return HTML rendered from the same validated packs the JSON routes return, plus HTMX fragments under the same paths when the request carries `HX-Request: true`. They introduce no additional mutation: the console posts to the two endpoints above and to nothing else.

**Live process.** `python -m aegis serve` (or `python -m services.api`) binds the JSON API and the HTML console. Assessment uses the stdlib server in `services/api/server.py`. When `requirements-ui.txt` (FastAPI, Jinja2, uvicorn) is installed, the same command prefers FastAPI and Jinja templates under `apps/web/templates/`. Scripts are limited to vendored `apps/web/static/htmx.min.js`.

Every route is read-only except those two. There is no route that mutates a source system, and none may be added — the compliance tripwire scans for exactly that, and the route inventory in AC-FR008-01 asserts the mutation set by name.

**Server-side gating.** The acknowledgement endpoint re-evaluates its own preconditions — every critical evidence item opened, segregation of duties satisfied — on the request itself. It never trusts that the interface withheld the control, so a direct HTTP call is refused exactly as a click would be. This is what makes BR-065 and BR-070a enforcement rather than presentation.
