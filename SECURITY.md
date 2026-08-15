# Security

## Secrets

`.env.example` lists variable **names** only. Never commit credentials, tokens, API keys, or real hostnames. Local key auth, if used at all, comes from a secret store — not from this repository.

## Default posture

- Deny by default. Authorisation is re-checked at execution time.
- `AEGIS_LLM_ENABLED=false` is honoured in every runtime mode.
- `authorized_context.execution` is `disabled` for graded runs; the kernel never executes a side effect.
- Challenge evidence is hash-verified. A mismatch abstains; it does not silently continue.
- Retrieved documents, tool descriptions, and user text are untrusted until status, authority, signature/hash, and applicability are verified.

## Reporting

Open a tracked finding in `security/exceptions/` rather than weakening a gate. Shrinking `packages/contracts/deny_list.json` is a build failure.
