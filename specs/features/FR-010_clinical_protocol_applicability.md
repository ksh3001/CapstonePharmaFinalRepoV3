# FR-010 — Clinical protocol applicability support

**Question this file answers:** which protocol version actually governs a given subject at a given site, and how to present eligibility evidence without deciding eligibility.

| Field | Entry |
|---|---|
| Workflow | Shared — clinical context |
| Contract | `advisory_nonexecuting.schema.json` for PUB-15 |
| Fixtures | PUB-15 (clinical) |
| Injects | 013, 014, 016, 017, 018, 019, 020 |
| Principles | AP-1, AP-2, AP-3, AP-4 |
| Owner | Clinical operations role, with GxP lead |
| Phase | 3 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

A clinical operations user asks which protocol context applies to a subject, and what the eligibility evidence says.

## 2. Preconditions

The subject resolves to a trial and a site · site approval records, protocol versions and protocol extracts are hash-verified · `as_of` is supplied.

## 3. Happy path

1. Resolve subject → trial → site.
2. Determine the protocol version **approved for that site**, with its ethics-committee status and effective date.
3. Retrieve the globally current version and any others, retaining all.
4. State which version governs locally and why, citing the site approval record rather than recency.
5. Present eligibility evidence verbatim with every reference range supplied and its origin.
6. Where reference ranges disagree, present all of them as a contradiction.
7. Emit with no eligibility conclusion.

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| Site-approved version differs from the globally current version | The site-approved version governs locally. Both are retained and the divergence is stated; global currency alone never proves local applicability (PUB-15) |
| A version is obsolete but still cached at the site | Reported as an active risk: obsolete, cached, and therefore possibly in use |
| Site approval for the current version is pending | The pending state is stated as a gap; pending is neither approved nor rejected |
| Reference ranges disagree — central, local and EDC-rule ULN all differ | All three retained with their sources as a contradiction. No range is chosen |
| A value sits between two applicable ranges | Presented as range-dependent, with the outcome under each range shown separately and no conclusion drawn |
| Consent withdrawn or mismatched for the subject | FR-005 gates apply; affected data is excluded and the exclusion is reported |
| Device timestamps show clock skew | Timestamps retained per source with the skew reported; no timeline is reconstructed by adjustment |
| Adjudication of an endpoint is outstanding | Reported as a gap; an unadjudicated endpoint is never treated as adjudicated |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-079** | Applicability is determined by trial, country, site, approval state and effective time — never by version recency | 013 |
| **BR-080** | Global and local protocol versions are both preserved. Nothing is overwritten, and the local one is not treated as out of date merely for being older | 013 |
| **BR-081** | The system never states or implies that a subject is eligible, ineligible, a screen failure or a protocol deviation. Those are investigator decisions | 014 |
| **BR-082** | Every reference range supplied by evidence is presented with its origin. Where ranges disagree, the disagreement is the answer | 014 |
| **BR-083** | An obsolete version still cached at a site is reported as a risk rather than filtered out as irrelevant | 013 |
| **BR-084** | Consent state is evaluated per purpose through FR-005 before any subject data is presented | 017 |
| **BR-085** | Timestamps from decentralised devices are preserved with their skew reported; no clock is corrected and no sequence is inferred from adjusted times | 018 |
| **BR-138** | For a blinded trial, treatment allocation is a sensitive segment under FR-005 BR-046: it is **absent** from every pack for every role, including roles otherwise highly entitled, because presence alone would unblind. The system additionally detects **inferential** unblinding — where a combination of permitted fields such as a characteristic laboratory shift, a dispensing record, an adverse-event pattern or a kit identifier would allow allocation to be deduced — and where that risk is present, withholds the combination, states that a combination was withheld without naming the discriminating value, and raises a potential-unblinding finding routed to the unblinding-authority role. The system never reveals, infers, confirms or denies an allocation, and never treats an already-unblinded record as licence to unblind another | 016 |
| **BR-139** | Endpoint assessments awaiting adjudication are reported as **pending** with the date the assessment entered the queue and the committee responsible. A pending assessment is never counted as adjudicated, never given a provisional value, and never omitted so that a dataset appears complete. An adjudication backlog is reported as a gap affecting every analysis that depends on it, and the system never adjudicates, predicts an adjudication outcome, or ranks cases by likely outcome | 019 |
| **BR-140** | Site-level risk indicators are presented as **observations with their evidence** — protocol deviations, query rates, enrolment anomalies, monitoring findings — each with its source and period, and each carrying the data-quality limitations of that source. The system never scores a site, never ranks sites against one another, never states that a site is non-compliant or should be inspected, audited or closed, and never presents an absence of findings as evidence of quality | 020 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR010-01** | The PUB-15 pack validates against `advisory_nonexecuting.schema.json` with zero errors | Contract test |
| **AC-FR010-02** | For `S-301-044` at site `IN-014`, the governing version is reported as **4.1**, citing `site_approvals.csv`, while **5.0** is reported as globally current and not locally approved | `T-BEHAV`, PUB-15, INJ-013 |
| **AC-FR010-03** | Version `3.2`, marked `obsolete_but_site_cached`, appears in the pack as a risk and is not silently dropped | `T-BEHAV`, PUB-15 |
| **AC-FR010-04** | The pending amendment state for `IN-014` appears as a gap, and no field states that 5.0 applies at that site | `T-GATE`, PUB-15 |
| **AC-FR010-05** | The ALT value `58 U/L` is presented with all three limits — `central_uln: 40`, `local_uln: 60`, `edc_rule_uln: 40` — each with its source, as a contradiction | `T-BEHAV`, PUB-15, INJ-014 |
| **AC-FR010-06** | No pack contains the words eligible, ineligible, screen failure, deviation or exclusion as a conclusion about a subject, at any nesting depth | `T-GATE` deny-list, INJ-014 |
| **AC-FR010-07** | The pack states that the value exceeds one limit and not another, **without** ranking the limits or selecting one | `T-BEHAV`, PUB-15 |
| **AC-FR010-08** | Subject data is withheld where consent for the purpose is withdrawn, and the withholding is reported | `T-GATE`, INJ-017 |
| **AC-FR010-09** | Device timestamps are preserved verbatim with skew reported and no adjustment applied | `T-ONT`, INJ-018 |
| **AC-FR010-10** | A protocol extract instructing the reader to take an action is treated as untrusted content and changes no output value | `T-GATE`, INJ-065 |
| **AC-FR010-11** | Three consecutive runs byte-identical; `ai_disabled` still produces a valid pack | Determinism, `T-RESIL` |
| **AC-FR010-12** | For a blinded subject, no allocation field appears in the payload for any role, verified against the response body rather than the rendered view; a fixture whose permitted fields would allow allocation to be deduced yields a withheld-combination statement that does not name the discriminating value, plus a potential-unblinding finding addressed to the unblinding-authority role | `T-GATE`, INJ-016 |
| **AC-FR010-13** | An endpoint awaiting adjudication renders as pending with its queue-entry date and responsible committee, is excluded from every adjudicated count, and raises a gap on each dependent analysis; no provisional or predicted outcome appears in any field | `T-BEHAV`, INJ-019 |
| **AC-FR010-14** | Site risk indicators render as observations with source, period and data-quality limitation, and the pack contains no site score, no ordering of sites and no inspection, audit or non-compliance recommendation; a site with no findings carries an explicit statement that absence of findings is not evidence of quality | `T-BEHAV`, INJ-020 |

## 7. AI and human boundary

AI may, when enabled, summarise the protocol context. It may not determine applicability, select a reference range, characterise a value as in or out of range for eligibility purposes, or suggest what the investigator should conclude. Applicability is computed deterministically from the site approval record.

## 8. Out of scope

Eligibility determination · screen-failure classification · protocol-deviation classification · unblinding · randomisation · endpoint adjudication · amendment approval.

## 9. Ambiguities

None blocking. Where the evidence supplies no site approval at all, the feature abstains on applicability rather than falling back to the global version.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `../data/data_model.md` §1 · master plan §5.4 (authority), §29.1 (identity resolution).
