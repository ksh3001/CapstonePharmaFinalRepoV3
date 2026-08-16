# Documentation register

**Question this file answers:** which document is authoritative for which question, in the FDE layering used by this build.

If two files disagree, the **spec** wins (`specs/`). The master plan holds rationale. These `docs/` files are the team-authored artefacts a reviewer, operator, or new engineer should read first.

## Layering (one question per file)

| Layer | Question | Start here |
|---|---|---|
| Product | What problem, for whom, what must never be decided | `product/intended-use.md`, `../specs/product/scope.md` |
| One-pager | Defence / intro slide (infographic) | `product/aegis-one-pager-infographic.pptx` |
| Architecture | Where code belongs | `architecture/overview.md`, `architecture/aegis-architecture.html` |
| ADR | Why a durable choice was made | `adr/` |
| Engineering | How to change the code without breaking gates | `engineering/developer-guide.md` |
| Quality | What must be green to call a run successful | `quality/release-bar.md` |
| Security | Default posture and how to report a finding | `security/posture.md`, `../SECURITY.md` |
| Operations | How to start, degrade, and stop | `operations/operator-guide.md` |
| Governance | AIMS scope and AI policy (not a certificate) | `governance/aims-scope.md`, `governance/ai-policy.md` |
| Compliance | What is checked vs certified | `compliance/eu-ai-act-iso-42001-status.md` |

## T-ARTEFACT product files

FDE injects that are answered by a versioned artefact plus a verifying test. Required header: **Inject** and **Obligation**. Do not leave unfinished markers in the body.

| Inject | Artefact | Verifying test |
|---|---|---|
| INJ-001 | `product/business-case.md` | `tests/compliance/test_benefit_claims.py` |
| INJ-002 | `product/success-metrics.md` | `tests/compliance/test_metric_conflicts.py` |
| INJ-003 | `product/no-ai-baseline.md` | `tests/compliance/test_no_ai_baseline.py` |
| INJ-004 | `product/patent-cliff.md` | `tests/compliance/test_artefact_docs.py` |
| INJ-078 | `product/vendor-concentration.md` | `tests/compliance/test_artefact_docs.py` |
| INJ-083 | `operations/vendor-exit.md` | `tests/compliance/test_artefact_docs.py` |
| INJ-084 | `operations/retirement.md` | `tests/compliance/test_artefact_docs.py` |

INJ-001…003 are also the closed artefact allow-list in `quality/static-analysis/inject_coverage_allowlist.json`. INJ-004 is additionally behavioural (BR-135 / AC-FR005-17).

## Workflow runbooks (inference off)

| Workflow | Runbook |
|---|---|
| Batch | `runbooks/batch_review.md` |
| PV | `runbooks/pv_intake.md` |
| Supply | `runbooks/supply_planning.md` |
| Incident | `../ops/runbooks/incident.md` |

## How to run the product

Root `README.md`. Do not put secrets in any file under `docs/`.
