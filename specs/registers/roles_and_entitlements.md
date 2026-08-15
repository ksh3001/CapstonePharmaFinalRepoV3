# Roles and entitlements register

**Question this file answers:** which roles the product recognises at runtime, what each may see and do, and where the entitlement decision gets its data.

This register exists because FR-005 §3 step 4 and BR-046 require entitlement to be checked "for the object class and for any sensitive segment within it", and nothing in the spec set said which role is entitled to which segment. A gate with no table behind it is the same defect class as a confidence rule with no number (plan §29): it reads as a control and implements as a guess.

## 1. Two populations, not one

The word "role" carries two distinct meanings in this build and they are never mixed.

| Population | Count | Where defined | Runtime authority |
|---|---|---|---|
| **Runtime roles** — who the product serves | **7** | This register | Determine what a request may see and which interrupts it may satisfy |
| **Accountability roles** — who owns the build | **6** | Plan §26 | Approve change classes; hold no runtime entitlement whatsoever |

An accountability role is a project function. A build-time Cursor agent (plan §32.4) is neither, and holds no entitlement in either population. The three sets are disjoint by construction, and `packages/config/roles.yaml` carries only the seven.

## 2. The seven runtime roles

Five come from `product/scope.md` §6. Two more are used by the feature specs and were previously undeclared, which is the gap this register closes.

| Role id | Business name | Primary features | Accountable for (`decision_rights.csv`) | AI authority |
|---|---|---|---|---|
| `qualified_person` | EU Qualified Person | FR-001, FR-008 | Batch certification | `none` |
| `safety_physician` | Safety Physician | FR-002, FR-008 | ICSR reportability | `none` |
| `supply_governance` | Supply Governance Board | FR-003, FR-008 | Stock allocation | `draft only` |
| `quality_reviewer` | Quality reviewer | FR-001, FR-004 | — contributes, does not certify | `none` |
| `security_privacy` | CISO / DPO | FR-005, FR-013, FR-014 | Consent and residency determinations | `none` |
| `auditor` | Auditor or inspector | FR-008, FR-014 | — read-only oversight | `none` |
| `unblinding_authority` | Unblinding authority | FR-010 | Unblinding decisions | `none` |

**`auditor`** is required by FR-008 §1, which names an auditor among the console's actors, and by FR-014, whose read path serves "a reviewer, auditor or inspector". It is **read-only in the strongest sense**: it may open any pack and any evidence chain within its residency scope, and it may satisfy **no** interrupt. An auditor who could acknowledge would be reviewing their own oversight.

**`unblinding_authority`** is required by BR-138, which routes a potential-unblinding finding to it by name. It is the only role that may receive such a finding, and — per BR-138 — even it receives **no allocation field**, because the product never reveals allocation to anyone. The role exists to receive the *finding*, not the value.

`supplier_quality_viewer` appears in `users_entitlements.csv` as `contractor_77` and is deliberately **not** a recognised role here. That fixture exists to be denied (PUB-09, INJ-060/061: IAM `revoked` against gateway `active_cached`). An unrecognised role is denied by default under BR-039, which is the correct outcome and needs no entry.

## 3. Role name canonicalisation

The package spells the same role two ways: `users_entitlements.csv` carries `qualified_person`, `decision_rights.csv` carries `EU Qualified Person`. This is the product's own identity problem turned inward, and it is resolved the way FR-004 BR-131 resolves any other local code — by scope, not by fuzzy match.

`role_id` above is canonical. Each source spelling maps to it through an **explicit, exhaustive** table in `packages/config/roles.yaml`; a spelling absent from that table is an unresolved identity and denies under BR-039 rather than being normalised by case-folding or whitespace-stripping. Silently equating `qualified_person` with `EU Qualified Person` would be exactly the naked-identifier merge that BR-129 forbids elsewhere.

## 4. Entitlement matrix — sensitive segments

`sensitive_segments.csv` gates by **access group**, not by role: `PV-1020` carries segments `pregnancy → PV_PREGNANCY` and `minor → PV_PAEDIATRIC`. The package supplies segment → access group and user → role, but **no role → access group edge**. That edge is a policy decision the package does not make, so it is a declared Unknown (AMB-15) with a fail-closed default rather than an invented mapping.

| Access group | Entitled roles | Basis |
|---|---|---|
| `PV_PREGNANCY` | `safety_physician` | Clinical necessity for causality assessment, which is the purpose the segment exists to serve |
| `PV_PAEDIATRIC` | `safety_physician` | As above |
| *any group not listed* | **none** | Deny by default — an unlisted group is unentitled for every role, including `auditor` |

Two properties are absolute regardless of the matrix. Entitlement is **absent, not redacted** (BR-046) — an unentitled role's pack does not contain the field, because a redaction marker discloses that the segment exists. And entitlement is checked **per purpose as well as per role** (BR-041), so `safety_physician` entitled to `PV_PREGNANCY` for causality assessment is not thereby entitled to it for a commercial purpose.

The matrix is data, not code: it lives in `packages/config/entitlements.yaml`, is loaded live per request under AP-9, and is never cached.

## 5. Segregation of duties

BR-070a requires segregation to be detected server-side. It is a constraint on **identity within a request**, not a role attribute, and it composes with the matrix rather than replacing it.

| Constraint | Rule |
|---|---|
| Preparer ≠ acknowledger | The identity that produced or last modified a pack may not acknowledge it, whatever its role |
| Attribution required | A shared or generic account satisfies no interrupt (BR-048), so it can be neither preparer nor acknowledger |
| Role sufficiency | The acknowledging identity must additionally hold a role entitled to that workflow's interrupt — being a different person is necessary, not sufficient |
| `auditor` exclusion | `auditor` satisfies no interrupt in any workflow, so it can never be an acknowledger |

"Preparer" and "acknowledger" are therefore **positions in a request**, not roles, and they appear nowhere in §2. Modelling them as roles would let a system grant someone the acknowledger role permanently and defeat the control.

## 6. What no role can do

No role, at any entitlement level, causes the product to decide batch disposition, determine ICSR reportability or causality, determine clinical eligibility, reserve or allocate stock, change quality status, or initiate a recall. Entitlement governs **visibility and the ability to record a human decision**; it never grants the system authority. `decision_rights.csv` sets `ai_authority` to `none` for every decision except stock allocation, which is `draft only` — and a draft is not an allocation.

This is why the register has no "administrator" or "superuser" row. There is no entitlement level at which the gates in FR-005 stop applying, and a role that could disable them would be the one role capable of invalidating the EU AI Act applicability claim (plan §23.3).

## 7. Sources and verification

| Concern | Source | Verified by |
|---|---|---|
| User → role, IAM and gateway state | `data/users_entitlements.csv` | AC-FR005-02, AC-FR005-05 |
| Role resolved live, never from cache | — | AC-FR005-12 |
| Decision → accountable role, AI authority | `data/decision_rights.csv` | The prohibited-action suite (§6 above) and AC-FR003-03 |
| Segment → access group | `data/sensitive_segments.csv` | AC-FR005-11 |
| Role → access group | `packages/config/entitlements.yaml` (AMB-15) | AC-FR005-11 |
| Source spelling → canonical `role_id` | `packages/config/roles.yaml` | AC-FR005-02, which requires the contractor's role to resolve before it can be denied |
| Attribution — no shared account satisfies an interrupt | Request state | AC-FR005-13 |
| Preparer ≠ acknowledger | Request state, server-side | AC-FR008-12 |

Adding a role, an access group or a matrix row is a **change-controlled edit** under the plan §23.4 change classes, because it alters who can see regulated evidence.
