# EU AI Act and ISO/IEC 42001 — status report

Source: this repository as of 15 Aug 2026, after the in-repo gap-fill. This is a repo review, not a legal opinion and not a notified-body or certification-body assessment.

## Verdict

**Neither framework is certified.** The engineering gaps from the first review are now closed as executable controls.

The product is not EU AI Act certified, not ISO/IEC 42001 certified, and the build plan still says no conformity assessment is claimed. CI now fails if the inherited advisory posture is broken.

| Question | Answer | What that means |
|---|---|---|
| EU AI Act compliant? | Not validated | No notified-body review. Posture is advisory / deployer lens only. |
| ISO/IEC 42001 certified? | Not validated | No AIMS certificate. Mapping and policy files now exist in-repo. |
| Checked in this repo? | Yes, internally | Control map + artefact 19 §7 tripwires run in `tests/compliance/`. |
| Safe to say in a demo? | Yes, if precise | Say: advisory system, human decides, tripwires defend the claim. Do not say certified. |

| Metric | Value |
|---|---|
| EU AI Act conformity assessment | No |
| ISO/IEC 42001 certification | No |
| Rows in `control-map.csv` | 23 |
| Internal tripwires in CI | Live |

## What the repo claims

Plan §23.1: advisory system, deployer lens, human Decide authority retained, autonomous high-risk decisioning excluded by design, **no conformity assessment claimed**.

## What was added

| Asset | Status |
|---|---|
| `docs/product/intended-use.md` | Present |
| `docs/governance/aims-scope.md` and `ai-policy.md` | Present |
| `compliance/iso42001/mapping.md` | Present |
| `ops/runbooks/incident.md` | Present |
| `compliance/control-map.csv` | Full §23 schema; each row has test + existing evidence file |
| `compliance/tripwires/evaluate.py` | Write tools, human review, model pin, residency, deny-list, thresholds, change classes |
| `tests/compliance/test_change_classes.py` | Present |
| `evals/thresholds.baseline.yaml` | Frozen hard gates |
| `compliance/eu-ai-act/model-registry.json` | Pinned advisory models |
| `compliance/eu-ai-act/residency-policy.json` | Analysed regions |

A failing tripwire prints `EU AI Act applicability claim invalidated — re-run artefact 19`.

## What you may say

**Accurate**

- AEGIS is designed as an advisory system. A human retains Decide authority.
- CI includes a control map and tripwires that fail if prohibited mutations, a missing review gate, an unpinned model, an off-policy region, a shrunk deny-list, or a loosened eval gate appear.
- The inherited posture is a claim to defend, not a certificate.

**Do not say**

- EU AI Act compliant / certified / conformity assessed.
- ISO 42001 certified or operating a certified AIMS.

## If you need a real validation later

Classify the system under the Act with counsel and engage a notified body or ISO auditor. This repository still does not issue that validation.
