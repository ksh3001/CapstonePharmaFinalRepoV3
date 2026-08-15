# FR-014 — Evidence store, integrity and retention

**Question this file answers:** what is written down for every request, how it is proven unaltered, how long it is kept, and how an inspector gets it back out.

| Field | Entry |
|---|---|
| Workflow | Shared — every request in every mode writes here |
| Contract | Writes `audit{}` into all contracts; the store itself is not a contract surface |
| Fixtures | All 15 |
| Injects | 029, 035, 036, 061, 062, 069, 077, 083, 084 |
| Principles | AP-3, AP-8, AP-9, AP-11, AP-12 |
| Owner | Architecture lead, with GxP / quality lead and the DPO role |
| Phase | 1, extended in 4 |
| Spec version | 1.1 — `outcome` record added, closing the structural reopen in `../../03_lean_dmaic/structural_reopen.md` §2.1 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

Not user-facing on write: every request writes automatically. On read, a reviewer, auditor or inspector retrieves a chain by `request_id`.

## 2. Preconditions

The store root is writable · the previous chain head is readable · retention rules and legal-hold state are readable **live**, never cached.

## 3. Happy path

1. Open a record for the request: identity, purpose, authorisation decision and inputs, mode, code version, `as_of`.
2. Record input artefacts with their SHA-256 and the copy-set manifest hash.
3. Record the emitted pack as canonical bytes with its hash.
4. In `advisory` mode, record the full model interaction and every guard outcome (FR-013).
5. Record every abstention, denial, gap and contradiction with its reason code.
6. Record reviewer actions as they occur.
7. Close the request with exactly one `outcome` record carrying its terminal disposition, whether or not a pack was emitted.
8. Seal each entry with the hash of the previous entry, extending the chain.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| The store is unwritable | The request **fails closed**. An action with no evidence is not an action this system takes |
| Chain verification finds a break | Reported with the first broken link. The chain is never silently repaired or re-sealed |
| A record would contain a secret or a direct identifier | Blocked at write time by a scan, and the block is itself recorded |
| A retention period expires while a legal hold is active | Expiry is refused; the hold wins and the refusal is recorded |
| A deletion request targets held records | Restriction, not deletion, per FR-005 BR-043 |
| Cloud store unreachable in `cloud` mode | Fall back to the local chain and reconcile on restoration; never drop the record |
| An index is lost or corrupted | Rebuilt from the store. The index is derived and disposable |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-114** | The store is append-only and content-addressed. There is no update and no delete path other than governed retention expiry | 036 |
| **BR-115** | Each entry carries the hash of the previous entry, so alteration or removal is detectable | 029, 036 |
| **BR-116** | A request that cannot write evidence does not proceed. Evidence is a precondition, not a by-product | 029 |
| **BR-117** | The record set is identical across modes; only the destination differs. `cloud` adds platform WORM, it does not add a different design | 084 |
| **BR-118** | No database is the system of record. Any index is derived from the store and rebuildable | 084 |
| **BR-119** | LLM prompt and response records expire at **90 days** unless an evidence or legal hold applies, per `data/retention_rules.csv` | 035, 062 |
| **BR-120** | Clinical source and ICSR records are retained and are never expired by this system | 035 |
| **BR-121** | Legal-hold state is read live at expiry time and blocks expiry. It is never cached | 061 |
| **BR-122** | An expiry is itself an event in the chain, so a deletion leaves a trace | 035 |
| **BR-123** | Evidence remains readable and verifiable with every vendor integration removed | 083, 084 |
| **BR-124** | No secret, credential or direct identifier is ever written to the store; a write-time scan enforces this | 062 |
| **BR-142** | Every request closes with exactly one `outcome` record carrying a disposition from the closed set `completed`, `abstained`, `denied`, `budget_exhausted`, `source_unavailable`, `contract_invalid`, `guard_failed`, `timeout`, `internal_error` — written whether or not a pack was emitted, and written even when the request failed. The first three are **deliberate dispositions** the system chose and each requires a matching `decisions` entry, so a request cannot be reported as abstaining without the abstention itself being recorded; the remaining six are **failures**. A failure that matches no other value is `internal_error`; it is never omitted, never recorded as a deliberate disposition, and never expressed as free text in place of a disposition. Free-text detail may accompany a disposition but never replaces one | 036, 077 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR014-01** | Every fixture run produces a complete chain containing request, inputs, pack, decisions and audit entries | `T-BEHAV`, all 15 |
| **AC-FR014-02** | `python -m aegis verify-evidence` passes on a clean run and reports the **first** broken link when any byte of any record is altered | `T-GATE`, INJ-036 |
| **AC-FR014-03** | Deleting one record from the middle of a chain is detected, naming the break point | `T-GATE`, INJ-029 |
| **AC-FR014-04** | A read-only store causes the request to fail closed, with no pack emitted | `T-RESIL` |
| **AC-FR014-05** | In `advisory` mode, every call stores prompt hash, rendered prompt, response, deployment, model version, `api-version`, tokens, cost, filter results and all five guard outcomes | `T-BEHAV`, FR-013 |
| **AC-FR014-06** | Scanning the whole store after a full fixture run finds zero secrets and zero direct identifiers | `T-SEC`, INJ-062 |
| **AC-FR014-07** | An LLM record older than 90 days with no hold expires, and the expiry appears as an event in the chain | `T-BEHAV`, INJ-035 |
| **AC-FR014-08** | The same record under an active legal hold does **not** expire, and the refusal is recorded | `T-GATE`, INJ-061 |
| **AC-FR014-09** | Hold state is read live at expiry; zero cache keys exist for hold or retention state | `T-SEC`, AP-9 |
| **AC-FR014-10** | Clinical source and ICSR records are never expired, proven by advancing the clock past every configured period | `T-BEHAV`, INJ-035 |
| **AC-FR014-11** | `python -m aegis evidence --request-id REQ-...` returns the complete chain, including what the model was told, in one command | `T-BEHAV`, DoD §7 |
| **AC-FR014-12** | The store is readable and verifiable with all vendor integrations uninstalled | `T-RESIL`, INJ-083, 084 |
| **AC-FR014-13** | Deleting the derived index and rebuilding it from the store reproduces it exactly | `T-RESIL` |
| **AC-FR014-14** | Record layout is byte-identical across `assessment`, `advisory` and `cloud` for the same request, excluding the model interaction that only `advisory` produces | `T-METRIC` |
| **AC-FR014-15** | In `cloud` mode the container carries a time-based immutability policy, and an overwrite attempt is rejected by the platform | `T-SEC` |
| **AC-FR014-16** | Every request in a full fixture run closes with exactly one `outcome` record — count of `outcome` records equals count of `request` records, including runs that emitted no pack. Every disposition is one of the nine values; a value outside the set fails validation. Every `abstained` and `denied` outcome reconciles one-to-one with a `decisions` entry, and a run whose failure cannot be classified renders `internal_error` rather than omitting the record | `T-BEHAV`, INJ-077 |

## 7. AI and human boundary

No model writes to, reads from, or influences the evidence store. Retention and hold decisions are deterministic and read live. A model may summarise a chain for a human in `advisory` mode, but the summary is annotation and the chain remains the record.

## 8. Out of scope

Being a general document management system · being a regulated records system under Part 11 or Annex 11 · e-signatures · archival beyond the declared retention periods · replacing any source system's own audit trail.

## 9. Ambiguities

None blocking. Tamper-**evidence** is claimed; tamper-**proofing** is not, because it would require infrastructure this project does not have. The distinction is stated wherever integrity is claimed.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `FR-004`, `FR-005`, `FR-007`, `FR-013` · `../data/state_transitions.md` · master plan §35.

`FR-007` is loaded because BR-057 reports cost per *successful* task and requires failed and abstained requests to stay in the denominator rather than be hidden from it. That rule needs a per-request disposition, and until BR-142 nothing wrote one — a rule in one feature depending on data another feature never recorded.
