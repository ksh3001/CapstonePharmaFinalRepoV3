# FR-013 — AI advisory generation and grounding (Azure OpenAI)

**Question this file answers:** how the system turns a computed pack into natural-language advice for a reviewer, and how that advice is prevented from becoming a decision, a fabrication or a leak.

| Field | Entry |
|---|---|
| Workflow | Shared — narrative layer over A, B, C and the advisory tasks |
| Contract | Writes only to `human_review.annotations`. **Adds no field to any regulated contract** |
| Fixtures | All 15, in `advisory` mode; narrative is compared against the offline pack |
| Injects | 064, 065, 070, 075, 076, 078, 079, 081, 082 |
| Principles | AP-1, AP-2, AP-3, AP-4, AP-6, AP-12 |
| Owner | Architecture lead, with the DPO role for the residency and retention controls |
| Phase | 4 |
| Spec version | 1.0 |
| Lifecycle stage | **1 — Defined.** Awaiting stage 2 validation |
| Reviewer | Pending |

## 1. Actor and trigger

Any user running in `advisory` mode. The narrative step runs **after** the pack is complete and validated — never before, and never in parallel with it.

## 2. Preconditions

The pack exists and is schema-valid · the kill switch is off · residency for the endpoint is permitted for this data and purpose · consent and entitlement gates have already passed · budget headroom exists · the deployment name and pinned model version resolve.

## 3. Happy path

1. Take the validated pack as the **only** input.
2. Minimise: pseudonymise identifiers and drop anything the purpose does not require.
3. Render a versioned prompt template; record its id and hash.
4. Check the cassette. On a hit, replay. On a miss in `advisory` mode, call Azure OpenAI with `temperature=0`, a fixed seed and a structured-output schema.
5. Run the output guard G-1…G-5.
6. On pass, attach the advice to `human_review.annotations`, visibly labelled as model-generated.
7. Write the full interaction to the evidence store (FR-014).

## 4. Exceptions

| Situation | Behaviour |
|---|---|
| Any guard check fails | Text discarded. Pack delivered without narrative, with the failing check named. **Never repaired, never re-prompted to "fix" it** |
| Azure unreachable, throttled or slow | Pack delivered without narrative and with a stated reason; bounded retries, no retry storm |
| Content filter triggers | Recorded as evidence; no re-prompt engineered around the filter |
| Residency check fails | The call is never made; the pack states why advice is absent |
| Budget exhausted | Budget-stop abstention; narrative is the first thing dropped, never a regulated field |
| Kill switch on | No call, in any mode, including `advisory` |
| Pack contains an abstention | Advice may explain the abstention. It may not narrate past it |
| Model returns nothing useful | Absence of advice is an acceptable outcome, stated plainly |

## 5. Business rules

| ID | Rule | Inject |
|---|---|---|
| **BR-099** | The model reads the finished pack and nothing else. It holds no retrieval tool, sees no raw source record, and can reach no document the deterministic layer did not already admit | 065 |
| **BR-100** | Model output reaches **only** `human_review.annotations`. No regulated field is ever written, amended or influenced by generated text | 006 |
| **BR-101** | Removing the model changes no regulated field. Proven by byte-comparison against the same run offline, not asserted | 082 |
| **BR-102** | Every number, date, identifier and unit in the advice must appear verbatim in the pack. Anything else is a fabrication and the output is discarded | 024, 065 |
| **BR-103** | Every evidence reference in the advice must resolve to an item already in the pack | 065 |
| **BR-104** | Advice carries no disposition, causality, eligibility, allocation or recall statement; the deny-list runs over generated text exactly as over computed text | 006 |
| **BR-105** | Advice is visibly labelled as model-generated wherever it appears, in the pack, the console and the export | EU AI Act transparency |
| **BR-106** | Personal data is pseudonymised and minimised **before** the prompt is built, not after the response returns | 062 |
| **BR-107** | The endpoint region is checked against the data's residency requirement before the call. A mismatch blocks the call. **Absent or unverified configuration is treated as a mismatch**, so the system fails closed rather than calling an unknown region | 064 |
| **BR-108** | Authentication uses Entra ID managed identity. No key appears in code, configuration, logs or evidence. Credentials are supplied by the environment or a secret store and are never committed | 070 |
| **BR-109** | Deployment name, explicit model version and `api-version` are pinned and recorded per call. Floating aliases are forbidden | 081 |
| **BR-110** | Every interaction is recorded in a cassette keyed by prompt hash plus deployment and model version. Tests and evals replay; only `advisory` calls live | 082 |
| **BR-111** | Prompt templates are versioned, hashed artefacts. A prompt change is change-controlled and triggers its own evaluation run | 081 |
| **BR-112** | Token, step and wallet budgets from FR-007 bind this feature; narrative is the first cost to be cut | 076 |
| **BR-113** | Azure OpenAI is disclosed as a single-vendor dependency wherever cost or risk is reported | 078 |

## 6. Acceptance criteria

| ID | Criterion | Verified by |
|---|---|---|
| **AC-FR013-01** | For all 15 fixtures, the pack produced in `advisory` mode is **byte-identical** to the pack produced in `assessment` mode once `human_review.annotations` is removed | `T-METRIC`, INJ-082 |
| **AC-FR013-02** | With the kill switch on, `advisory` mode produces a valid pack with no narrative and no outbound call, verified by a network assertion | `T-RESIL`, INJ-082 |
| **AC-FR013-03** | Advice containing a number absent from the pack is discarded, and the rejection is recorded with check `G-3` | `T-GATE` |
| **AC-FR013-04** | Advice citing an evidence id absent from the pack is discarded, recorded with check `G-2` | `T-GATE` |
| **AC-FR013-05** | Advice containing deny-list language is discarded, recorded with check `G-1`; the pack is still delivered | `T-GATE`, INJ-006 |
| **AC-FR013-06** | Advice that narrates past an abstention is discarded, recorded with check `G-5` | `T-GATE` |
| **AC-FR013-07** | A prompt-injection string inside a source document reaches neither the prompt nor the output, and the pack is byte-identical to the clean run | `T-GATE`, INJ-065 |
| **AC-FR013-08** | No direct identifier appears in any rendered prompt, verified by scanning stored prompts across all fixtures | `T-SEC`, INJ-062 |
| **AC-FR013-09** | A residency mismatch between the data requirement and the endpoint region blocks the call; zero outbound requests are made | `T-SEC`, INJ-064 |
| **AC-FR013-10** | No API key appears in source, configuration, logs, cassettes or evidence; the adapter fails closed if only key auth is available in a non-development mode | `T-SEC`, INJ-070 |
| **AC-FR013-11** | Deployment, model version, `api-version` and `system_fingerprint` are present in every stored interaction | `T-BEHAV`, INJ-081 |
| **AC-FR013-12** | A configured floating alias instead of a pinned version fails the build | `T-ARTEFACT`, INJ-081 |
| **AC-FR013-13** | Replaying cassettes produces byte-identical advice across three runs; the eval suite makes zero live calls | `T-METRIC`, NFR-21 |
| **AC-FR013-14** | With Azure returning 429 then 503, the pack is delivered without narrative, the reason is stated, and retries stay within the declared bound | `T-RESIL`, INJ-079 |
| **AC-FR013-15** | Exceeding the token ceiling drops narrative before any regulated content is affected | `T-RESIL`, INJ-076 |
| **AC-FR013-16** | Every annotation is labelled as model-generated in the pack, the console and the export | `T-UX`, EU AI Act transparency |
| **AC-FR013-17** | Content-filter results are stored for every call, including calls that returned no content | `T-BEHAV` |
| **AC-FR013-18** | A groundedness eval over all fixtures reports zero unsupported claims at the release gate; the gate is deterministic, not judge-scored | `T-METRIC`, NFR-22 |
| **AC-FR013-19** | With endpoint, deployment, model version or region unset, the system makes **zero outbound calls**, names the missing setting, and still delivers a valid pack. No region, model or endpoint is ever defaulted | `T-GATE`, AMB-14 |

## 7. AI and human boundary

This feature is the only place a model runs at all. Its entire output is commentary attached to a decision the deterministic layer already made and a reviewer will act on. The model cannot call a tool, choose a step, retrieve a document, write a regulated field or influence a gate. A reviewer may ignore the advice entirely and lose no information, because everything the advice discusses is already in the pack.

## 8. Out of scope

Model fine-tuning · retrieval-augmented generation over raw sources · agentic tool use by the model · chat with the data · model-driven routing · using the model to resolve any contradiction, gap or abstention.

## 9. Ambiguities

**AMB-13** — whether the Azure deployment holds the Limited Access exemption from abuse monitoring. **Confirmed open by the product owner; the safe default stands**: assume no exemption, send only pseudonymised content. The owner is the DPO role, and the decision is recorded in `compliance/eu-ai-act/`. This is a live processing decision, not a platform detail: without the exemption, prompts are retained by the provider for human review.

**AMB-14** — endpoint, deployment name, model version and region are pending; credentials will be supplied by the product owner. Until then there is **no default**, and the system fails closed per AC-FR013-19. Configuration slots are named in master plan §34.4 so that supplying them is a settings change, never a code change.

## 10. Specs to load when implementing

`../product/scope.md` · this file · `FR-014` · `../api/api_contracts.md` · `../nfrs.md` NFR-21…NFR-24 · master plan §34.
