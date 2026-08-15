# Security posture

**Question this file answers:** what the default security posture is, and where a finding goes.

Root `SECURITY.md` is the short form. This file is the operator/engineer form.

## Default

- Deny by default. Authorisation, consent, residency, and legal-hold are re-checked at execution time and are never cached (AP-9).
- `AEGIS_LLM_ENABLED=false` is honoured in every mode.
- Graded runs do not execute a side effect. `authorized_context.execution` is disabled.
- Challenge evidence is hash-verified. A mismatch abstains.
- Retrieved text, tool descriptions, and user prompts are untrusted until status, authority, signature/hash, and applicability are verified.
- Console mutations are acknowledge and contest only (`tests/security/test_no_action_controls.py`).

## Secrets

`.env.example` lists names only. Never commit keys, tokens, or real hostnames. Local key auth, if used, requires `AEGIS_ALLOW_KEY_AUTH=dev` and is not a grading path.

## Reporting

Open a tracked finding under `security/exceptions/` rather than weakening a gate. Shrinking `packages/contracts/deny_list.json` fails the baseline. Adding a write tool fails the artefact-19 tripwire.
