# State transitions

**Question this file answers:** which states exist, what moves between them, and which transitions are forbidden.

Four state machines matter. None of them models a regulated decision — that is the point.

## 1. Readiness state (Workflow A)

Values are fixed by the challenge contract: `insufficient_evidence`, `conflicted_evidence`, `ready_for_authorized_review`.

It is **computed on every run, never stored and never transitioned by a user action.** Precedence per BR-006:

```
any blocking gap or unresolved required element  → insufficient_evidence
else any unresolved contradiction                → conflicted_evidence
else                                             → ready_for_authorized_review
```

| Rule | Statement |
|---|---|
| Recomputation | Changing evidence changes the state on the next run; there is no transition event and no history of state changes to maintain |
| No override | No user, role or API can set this value. There is no endpoint that accepts it |
| Not a disposition | `ready_for_authorized_review` means a human can now review. It never means released, approved or acceptable (BR-007) |
| Monotonicity | Not guaranteed, and deliberately so — new contradicting evidence must be able to move a batch back from `ready_for_authorized_review` |

## 2. Request lifecycle

```
received → authorised → budgeted → executing → [awaiting_human] → packaged → emitted
                ↓            ↓          ↓              ↓
             denied     budget_stop  abstained    cancelled
```

| Transition | Rule |
|---|---|
| `received → authorised` | Execution-time check, never cached (AP-9). Failure emits a valid pack with `authorization.decision = "deny"`, not an HTTP error |
| `→ budget_stop` | Emits a partial pack with a budget-stop abstention; never a truncated answer presented as complete |
| `→ abstained` | A terminal *success* state. An abstention pack is a valid, schema-conformant deliverable (AP-4) |
| `executing → awaiting_human` | Raised by `interrupt()`; the thread is checkpointed before the pause |
| Any state → `emitted` | Only through contract validation. An invalid pack is never emitted |
| Re-entry | Replaying an emitted request with the same idempotency key returns the original pack (BR-030) |

`execution_status` is `not_executed` in every state, including terminal ones. It is a constant, not a variable.

## 3. Checkpoint / thread lifecycle (orchestrator)

```
new → active → suspended(interrupt) → resumed → completed
                      ↓                              ↓
                    stale                        replayable
                      ↓
              human_confirm_required
```

| Rule | Statement |
|---|---|
| Persist point | Before each step, `durability="sync"` (§20.4) |
| Freshness | Checkpoint age and content hash are validated before resume. Stale or mismatched → `human_confirm_required`, never a silent resume (INJ-080) |
| Content | References, hashes, ontology decisions and budget counters only. No PHI, enforced by a scanning test |
| Resume identity | Requires a valid reviewer identity; an anonymous resume is refused |
| Retention | TTL bounded. A DSR restriction marks a thread non-resumable rather than deleting a GxP-relevant trace (INJ-061) |
| Terminal | `completed` threads are replayable but never re-executable |

## 4. Human review lifecycle

```
pack_presented → evidence_opened → acknowledged → (reviewer acts outside AEGIS)
        ↓
    contested
```

| Rule | Statement |
|---|---|
| Forced view | `acknowledged` is unreachable until every critical evidence item has been opened (INJ-071) |
| Acknowledgement | A workflow event in the audit trail. **Explicitly not a 21 CFR Part 11 / Annex 11 signature** (plan §11) |
| Contest | Available from any state; recorded with reason and never suppressed |
| Terminal boundary | The lifecycle ends at `acknowledged`. What the reviewer then does — release, report, allocate — happens in a system of record that AEGIS cannot reach |

## 5. Gate outcomes (advisory contract)

`advisory_only` · `gate_enforced` · `abstained` · `escalated` · `partial_coverage`. These are outcomes of a single evaluation, not a machine with transitions: a run produces exactly one, and it is recomputed rather than updated.

## 6. Forbidden transitions

There is no transition, in any of these machines, that sets a disposition, confirms a signal, decides eligibility, allocates stock, changes quality status or initiates a recall. Those states are not modelled (`data_model.md` §5), so the transition is not merely blocked — it is unrepresentable.
