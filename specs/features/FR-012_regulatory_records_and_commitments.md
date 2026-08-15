# FR-012 — Regulatory records, identity and commitments

**Question this file answers:** how product identity, labelling, submission records and regulatory commitments are reconciled across systems that each believe they are authoritative.

Authored because dimension D07 — injects 045 to 050 — had no owning feature in the original index. The injects were mapped to test classes in plan §15, but no feature claimed the behaviour, so nothing would have been specified before it was built.

| Field | Entry |
|---|---|
| Workflow | Shared — regulatory context for A, B and C |
| Contract | `advisory_nonexecuting.schema.json`, `workflow: "regulatory"` |
| Fixtures | None public. Verified against `data/` regulatory sources and derived scenarios |
| Injects | 045, 046, 047, 048, 049, 050 |
| Principles | AP-1, AP-3, AP-4, AP-7 |
| Owner | Regulatory affairs role, with architecture lead |
| Phase | 3 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

A regulatory strategist asks which product identity, label text, submission state or commitment applies for a market, or an inspection request arrives and evidence must be assembled quickly.

## 2. Preconditions

RIM, ERP, labelling, submission and commitment sources are readable and hash-verified · the market or jurisdiction is stated · `as_of` is supplied.

## 3. Happy path

1. Resolve product identity across systems using the tiered strategy in plan §29.1.
2. Where identifiers disagree, emit an `IdentityConflict` rather than selecting a winner.
3. Retrieve label text per market with its version and approval state.
4. Retrieve submission sequence records and check continuity.
5. Retrieve commitments with their deadlines, deadline basis and owning authority.
6. Assemble the requested evidence set with provenance intact.
7. Emit with no submission, classification or commitment decision.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| RIM and ERP disagree on product identity | `IdentityConflict` citing both, with the fields that differ. No golden record is created and no system is declared authoritative |
| Label text differs between markets | Both retained per market with version and approval state. Divergence is expected and is reported, never reconciled into one text |
| A commitment deadline is ambiguous — relative to submission, approval or notification | All candidate deadlines retained with their basis and source. The system does not choose the operative date |
| A submission sequence number is missing | Reported as a sequence gap naming the missing number. Not renumbered, not assumed withdrawn |
| Variation classification is disputed between parties | Both positions retained with their rationale and source. Classification is a regulatory judgement |
| An inspection request arrives with a short deadline | Evidence is assembled and gaps are reported honestly. Deadline pressure never converts a gap into an assertion |
| Evidence for an inspection cannot be completed in time | The pack states what is unavailable and why, rather than presenting a partial set as complete |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-092** | Product identity conflicts across RIM, ERP and IDMP representations are surfaced as conflicts. No master record is synthesised and no source is ranked | 045 |
| **BR-093** | Labelling is presented per market with version, approval state and effective date. Cross-market divergence is a reported fact, not a defect to be corrected | 046 |
| **BR-094** | Every commitment is presented with its deadline, the basis for that deadline and the owning authority. Where the basis is ambiguous, all candidates are retained | 047 |
| **BR-095** | Submission sequence gaps are reported as gaps with the missing identifiers named. Sequences are never renumbered or inferred | 048 |
| **BR-096** | Variation classification disputes retain every position with its rationale. The system never classifies a variation | 049 |
| **BR-097** | Under inspection-driven time pressure the system's behaviour is unchanged: the same gates, the same abstentions, the same evidence standard. Urgency is not an input to any rule | 050 |
| **BR-098** | No pack asserts that a submission was made, accepted, approved or withdrawn, or that a commitment was met | 047, 048 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR012-01** | Team-derived regulatory scenarios emit `workflow: "regulatory"` and validate against `advisory_nonexecuting.schema.json` with zero errors | Contract test |
| **AC-FR012-02** | Conflicting product identifiers across two systems produce an `IdentityConflict` citing both, with the differing fields named and no winner selected | `T-ONT`, INJ-045 |
| **AC-FR012-03** | Divergent label text across two markets appears as two entries with version and approval state, and no merged text exists in the pack | `T-BEHAV`, INJ-046 |
| **AC-FR012-04** | A commitment with an ambiguous deadline basis yields all candidate deadlines, each with its basis and source, and no single operative date | `T-BEHAV`, INJ-047 |
| **AC-FR012-05** | A missing submission sequence number produces a gap naming the missing identifier | `T-BEHAV`, INJ-048 |
| **AC-FR012-06** | A disputed variation classification retains both positions and contains no classification statement | `T-GATE`, INJ-049 |
| **AC-FR012-07** | An inspection-surge scenario produces byte-identical output to the same scenario run without the urgency signal, proving urgency changes nothing | `T-GATE`, INJ-050 |
| **AC-FR012-08** | No pack contains submission, approval, acceptance, withdrawal or commitment-met language, at any nesting depth | `T-GATE` deny-list |
| **AC-FR012-09** | Every regulatory fact carries source, authority, version and effective date | Contract test |
| **AC-FR012-10** | Three consecutive runs byte-identical; `ai_disabled` still produces a valid pack | Determinism, `T-RESIL` |

## 7. AI and human boundary

AI may, when enabled, summarise a divergence in readable prose. It may not resolve an identity conflict, choose a deadline basis, classify a variation, or judge a commitment met. Regulatory judgement is the regulatory professional's.

## 8. Out of scope

Filing submissions · publishing labels · classifying variations · agreeing commitments · responding to an authority · creating a master data record.

## 9. Ambiguities

None blocking. Where no public fixture exercises a behaviour, the scenario is derived from `data/` sources and is labelled team-derived in the coverage record — the result is reported as team-derived rather than fixture-verified.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../data/data_model.md` · master plan §29.1 (identity resolution), §15 (inject map D07).
