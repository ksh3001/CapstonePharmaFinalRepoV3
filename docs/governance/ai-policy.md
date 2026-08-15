# AI policy (ISO/IEC 42001 clause 5)

Deterministic-first. No transfer of Decide authority.

## Policy statements

1. Engines classify. Agents sequence. A human decides.
2. Generative AI, when enabled, may only write labelled advisory annotations. It must not write a regulated field.
3. `assessment` and `ai_disabled` remain sufficient to produce a schema-valid pack.
4. No role may disable the FR-005 gates. There is no administrator entitlement that turns the product into an actor in a system of record.
5. Prohibited-action language and mutating console controls other than acknowledge and contest fail the build.
6. Model identity is pinned. Floating aliases (`latest`, `current`, `alias`) are refused.
7. Failed gates become fixtures. Incidents use `ops/runbooks/incident.md` and `templates/incident-record.md`.

## Leadership

Accountability roles in plan §26 own the build. Runtime roles in `specs/registers/roles_and_entitlements.md` own review. Individual names remain pending (A-001). The roles bind regardless.

This policy does not certify an AIMS. It is the in-repo rule the tripwires enforce.
