# Vendor exit

**Inject:** INJ-083 (vendor exit deadline).  
**Obligation:** evidence and audit artefacts remain readable, and packs remain reproducible, with all vendor integrations removed.

## Exit path

1. Set `AEGIS_RUNTIME_MODE=assessment` or `ai_disabled` and `AEGIS_LLM_ENABLED=false`.
2. Do not install `requirements-ui.txt` if the question is “can the engines still run”. For a console-only exit, keep UI extras and leave inference off.
3. Unset Azure, Redis, and MCP environment variables.
4. `python -m aegis setup` then `python -m aegis run --workflow batch --id NCB204-B24071`.
5. `python -m aegis evidence-export` and `python -m aegis verify-evidence`.

The stdlib runner is authoritative (ADR-008). LangGraph and Azure OpenAI are optional.

## What must still work

Schema-valid packs for the three workflows. Hash-linked evidence chain. Deny-list. Kill switch. No call to a vendor host.

## Stop if the claim drifts

A release that cannot produce a pack after the vendor is removed has failed AC-FR009-12 / AC-FR014-12. Do not paper over it with a cassette.
