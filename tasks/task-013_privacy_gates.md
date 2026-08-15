# TASK-013 — Privacy and purpose gates

**Goal:** evaluate consent, residency, DSR versus hold, sensitive segments and per-purpose pseudonymisation live, never from cache. Denials are schema-valid packs with no withheld content.

## Specs to load

FR-002 BR-012 / BR-012a / BR-017 · FR-005 BR-041–047 · `specs/data/data_model.md` §1 · `specs/registers/roles_and_entitlements.md` §4 · AMB-15 · plan §23.

Do not implement IAM cache vs revoke (TASK-005). Do not implement tool-manifest signing (TASK-023). Do not implement the evidence-store retention engine (TASK-034) beyond the PUB-11 hold check.

## Out of scope

Performing deletions · filing DSR responses · changing consent records · approving transfers · re-identification combination refusal (AC-FR005-19).

## Steps

1. Purpose must be in the register. Unregistered purposes are named and denied.
2. Consent is per purpose at `as_of`. `withdrawn_biomarker` blocks biomarker and leaves trial available. `cached_active` processing is a control failure.
3. Open DSR vs active hold → restriction, both obligations documented, never deletion.
4. AI prompt-log 90-day expiry is not applied while a hold is active; the hold check is shown.
5. Residency and unapproved exports deny the path; no case content in the denial pack.
6. Sensitive segments are absent (not redacted) unless the role is entitled. Unlisted groups are unentitled for every role.
7. Direct identifiers are replaced by a SHA-256 purpose-scoped pseudonym. The mapping never leaves the kernel; the transformation is audited.
8. Authorisation, consent, residency and hold state cannot be written to any cache namespace.

## Done when

`python -m aegis test` is green; PUB-11 documents DSR-17 vs LH-44 as restriction; a biomarker-purpose request loads no subject content.
