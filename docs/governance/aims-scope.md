# AIMS scope (ISO/IEC 42001 clause 4)

This document scopes the AI management system **for this repository**. It is not an ISO/IEC 42001 certificate and not a claim that a certified AIMS is in operation.

## Context

AEGIS is an advisory evidence product. The inherited EU AI Act posture (plan §23.1) is: advisory system, deployer lens, human Decide authority retained, autonomous high-risk decisioning excluded by design, no conformity assessment claimed.

## Scope of the AIMS in this repo

In scope: design, build, test, and change-control of the AEGIS codebase, including optional Azure OpenAI narrative annotations behind `InferencePort`.

Out of scope: live MES / LIMS / QMS / safety systems of record; batch release; PV medical decisioning; stock-movement; notified-body assessment; organisational ISO certification.

## Interested parties

| Party | Interest |
|---|---|
| Reviewer roles in `roles_and_entitlements.md` | A reviewable pack without a transferred Decide |
| Deployer (EU lens) | Advisory posture that does not silently become high-risk automation |
| Assessors / graders | Executable tripwires and a control map, not a legal opinion |
| Patients / public | The product must not weaken Quality authority (INJ-001) |

## Boundaries

- Deterministic engines in `packages/domain` are the source of truth (AP-1).
- The UI is a consumer (AP-10).
- Assessment mode installs nothing and runs offline (AP-5).
- A change that adds a write tool, removes forced review, unpins a model, leaves the analysed region, shrinks the deny-list, or loosens a hard eval gate invalidates the inherited applicability claim (artefact 19 §7).
