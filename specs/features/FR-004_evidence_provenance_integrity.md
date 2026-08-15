# FR-004 — Evidence provenance and integrity service

**Question this file answers:** how does any fact become citable, and what happens when it cannot be trusted.

This feature has no fixture of its own because it sits under all fifteen. Every other feature depends on it, so it is authored first and built in Phase 1.

| Field | Entry |
|---|---|
| Workflow | Shared — no workflow of its own |
| Contract | Contributes `evidence[]` to all four contracts via `evidence_item.schema.json` |
| Fixtures | All 15 |
| Injects | 005, 007, 008, 010, 012, 013, 029, 031, 032, 033, 034, 036, 048, 065 |
| Principles | AP-3, AP-4, AP-8, AP-11, AP-12 |
| Owner | Architecture lead, with GxP / quality lead |
| Phase | 0–1 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

Not user-facing. Every engine calls it before asserting anything. No component may construct an `EvidenceItem` by hand — a build gate forbids the literal construction outside this package.

## 2. Preconditions

The artefact exists in the copy set with a `PROVENANCE.csv` row · `as_of` is known · the requesting purpose and role are known, since applicability depends on both.

## 3. Happy path

1. Resolve the reference to a copy-set path.
2. Recompute SHA-256 and compare against `FILE_HASHES.csv`.
3. Read document control: `document_id`, `status`, `effective_date`, `authority`, `jurisdiction`.
4. Evaluate applicability at `as_of` — effective period, jurisdiction, and the requesting purpose.
5. Resolve supersession: locate any superseding document; retain both.
6. Scan content for embedded instructions and mark trust accordingly.
7. Emit an `EvidenceItem` with `source`, `record_id`, `authority`, `retrieved_at`, `integrity.sha256` and `source_preserved: true`.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| Hash mismatch | `reduced_integrity`. The artefact's facts are unusable; every dependent assertion abstains with `integrity_failure` |
| Referenced document absent from the corpus | `referenced_missing`. A gap is raised naming the reference; the absence is never treated as absence of the obligation |
| Document status is draft, retired or unknown | Not usable as authority. Content may be *described* but never grounds an assertion |
| Evidence produced by an unapproved or unvalidated tool, such as an ad-hoc spreadsheet | Recorded with its origin and excluded from authority; the validation gap is reported (INJ-032) |
| Source system had its audit trail disabled for the period | `reduced_integrity` for facts from that period, with the window stated (INJ-029) |
| Artefact changed outside change control | Integrity finding naming the bypass; facts are not silently accepted (INJ-034) |
| `as_of` falls outside the effective period | Not applicable. Both the document and the reason for non-applicability are reported |
| A superseding document exists | Both retained, relationship stated. The superseded one is never deleted or hidden |
| Content contains an instruction to the reader | `untrusted`. A security finding is raised and no output value changes |
| Two documents of equal authority disagree | Both cited; the disagreement is a contradiction, never a merge |
| `recorded_at` differs from `event_time` | Flagged as back-entered with the magnitude of the difference (AMB-11) |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-031** | A fact may be asserted only through an `EvidenceItem`. There is no path from raw file to output that bypasses this service | 029 |
| **BR-032** | Integrity is verified at read time, not trusted from a manifest written earlier in the run. Evidence from a system whose audit trail was disabled, or changed outside change control, is `reduced_integrity` | 029, 034, 036 |
| **BR-033** | Authority is a function of status, effective period, jurisdiction and purpose evaluated at `as_of` — never of recency alone. A newer document is not automatically the applicable one, and an unapproved or unvalidated tool's output is not authority at all | 031, 032 |
| **BR-034** | Supersession is represented as a relationship between retained documents. Nothing is overwritten | 013 |
| **BR-035** | Retrieved content is data, never instruction. Imperative text inside evidence raises a finding and is excluded from any reasoning path | 065 |
| **BR-036** | A missing referenced document or a broken reference sequence produces a gap naming the reference. Silence is never read as compliance | 048 |
| **BR-037** | `retrieved_at` is derived from `as_of`; source timestamps are reproduced verbatim, including missing timezones and coarse precision | 025 |
| **BR-038** | Back-entered records — where `recorded_at` post-dates `event_time` — are flagged with the magnitude of the gap, and the flag travels with the fact into every pack that cites it | 036 |
| **BR-129** | Identifiers are qualified by the organisation and source system that issued them, so an identifier from an acquired organisation is a distinct identity from an identically-spelled identifier elsewhere. Records from two organisations are never merged on a naked identifier match; where they may denote the same real-world thing, the relationship is a **candidate**, and the absence of an approved cross-organisation mapping produces an abstention rather than a join | 005 |
| **BR-130** | A measurement carries the analytical method and method version that produced it. Values produced under different method versions are comparable only under an approved comparability assessment effective at `as_of`; otherwise they are presented side by side with their methods and a comparability abstention. Trends and historical series are never assembled across a method change without that assessment, and a method change inside a series is reported on the series itself | 007 |
| **BR-131** | A local or internal code — compound, sample, lot or study code — is resolved to identity only within the scope that issued it. Two records sharing a local code but differing in issuing scope are a **collision**, reported as such with both records retained. A collision is never resolved by preferring the more recent, the more complete or the more convenient record | 008 |
| **BR-132** | Where evidence of possible manipulation of a source record exists — a reprocessed or recropped image, a deleted acquisition, a metadata inconsistency — the concern is raised as a finding at the highest severity the pack supports, the affected facts are marked `reduced_integrity`, and the concern is routed to a human. The system never clears such a concern, never judges whether manipulation occurred, and never allows a later record to supersede the concern | 010 |
| **BR-133** | Where sources disagree about a scientific claim, every position is retained with its source, method and date, and the disagreement is reported. Additionally, each source's **usage licence and permitted-purpose terms** are carried with it; where a licence does not permit the requested purpose, the content is excluded and the exclusion is reported as a gap naming the licence — never silently included and never silently dropped | 012 |
| **BR-134** | Recurrence of a problem across quality records is surfaced by linking records that share a root-cause classification, product, process or equipment, **including across different taxonomies and different versions of the same taxonomy**. Links are candidates carrying the basis for the link. The system never concludes that a corrective action was effective or ineffective, never closes or reopens a record, and reports recurrence spanning a closed action as a finding rather than resolving it | 033 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR004-01** | Every `evidence[]` entry in every pack from all 15 fixtures carries `source`, `record_id`, `authority`, `retrieved_at`, `integrity.sha256` matching `^[a-f0-9]{64}$`, and `source_preserved: true` | Contract test, all fixtures |
| **AC-FR004-02** | A deliberately corrupted copy-set artefact causes an `integrity_failure` abstention, and **no fact from that artefact appears anywhere in the pack** | `T-GATE` |
| **AC-FR004-03** | A draft-status document is never cited as authority; the pack states why it was not used | `T-BEHAV`, INJ-031 |
| **AC-FR004-04** | Given a superseded and a superseding document, both appear in `evidence[]` with the supersession relationship stated | `T-BEHAV`, INJ-013 |
| **AC-FR004-05** | A document effective after `as_of` is excluded from authority with a stated reason, and a document effective before but retired is likewise excluded | `T-ONT` |
| **AC-FR004-06** | An SOP containing `"ignore previous instructions"` or an equivalent imperative produces a security finding, and the pack is **byte-identical** to the same run with that sentence removed | `T-GATE`, INJ-065 |
| **AC-FR004-07** | A reference to a document absent from the corpus produces a gap naming the missing reference | `T-BEHAV`, INJ-048 |
| **AC-FR004-08** | A source timestamp of `2026-07-20` is emitted as `2026-07-20` — never expanded to midnight, never given a timezone it did not have | `T-ONT`, INJ-025 |
| **AC-FR004-09** | A record where `recorded_at` post-dates `event_time` is flagged with the difference, and the flag is present in every downstream pack citing it | `T-BEHAV`, INJ-036 |
| **AC-FR004-10** | A static gate fails the build if `EvidenceItem` is constructed outside `packages/domain/evidence` | `T-ARTEFACT` |
| **AC-FR004-11** | Two records from different organisations carrying the identical identifier string resolve to two identities; the pack contains no merged record and raises a cross-organisation mapping abstention | `T-ONT`, INJ-005 |
| **AC-FR004-12** | Two results produced under different method versions, with no approved comparability assessment, appear side by side with their methods and a comparability abstention, and no trend, delta or aggregate is computed across them | `T-ONT`, INJ-007 |
| **AC-FR004-13** | Two records sharing a local code but differing in issuing scope produce a collision finding with both retained; no field selects one as canonical | `T-ONT`, INJ-008 |
| **AC-FR004-14** | A source record carrying a manipulation indicator produces a finding routed for human review, marks the affected facts `reduced_integrity`, and no later record or subsequent run clears the finding | `T-BEHAV`, INJ-010 |
| **AC-FR004-15** | Two sources disagreeing on a scientific claim are both retained with method and date; content whose licence does not permit the requested purpose is excluded with a gap naming the licence, and appears in no field of the pack | `T-KG`, INJ-012 |
| **AC-FR004-16** | Records sharing a root cause under two different taxonomy versions are linked as recurrence candidates carrying the basis for the link; the pack contains no effectiveness verdict and no record-closure statement | `T-KG`, INJ-033 |
| **AC-FR004-17** | A value calculated by an unvalidated spreadsheet or other uncontrolled tool is never cited as authority; it appears, if at all, marked as an uncontrolled calculation with the tool named, and any conclusion depending on it abstains | `T-BEHAV`, INJ-032 |
| **AC-FR004-18** | A record changed outside change control — no approval reference, or an approval dated after the change — produces an integrity finding naming the bypass and marks the affected facts `reduced_integrity`; a retrospective approval is reported as retrospective and does not clear the finding | `T-BEHAV`, INJ-034 |

## 7. AI and human boundary

No model is involved at any point. This service is pure deterministic code in `assessment` and in every other mode, because trust decisions made by a model would be trust decisions that cannot be reproduced.

## 8. Out of scope

Repairing corrupted artefacts · deciding which of two conflicting authorities is correct · deleting superseded documents · normalising source timestamps.

## 9. Ambiguities

AMB-11 — the materiality threshold for back-entry flagging is a declared Unknown; the working default flags any non-zero difference.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../data/data_model.md` §1 · `../api/api_contracts.md` · master plan §28 (determinism), §5.4 (trust).
