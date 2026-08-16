# Operator guide

**Question this file answers:** how to start, degrade, and stop a running console.

## Start (local)

```text
python -m pip install -r requirements-ui.txt
python -m aegis setup
python -m aegis serve --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/ . Liveness on Azure: `/healthz`. Full operator steps for App Service: `azure-webapp.md`.

Without UI extras the stdlib server still serves HTML. FastAPI is the intended console transport.

## Degrade

| Intent | Setting |
|---|---|
| Model off, console on | `AEGIS_RUNTIME_MODE=ui` and `AEGIS_LLM_ENABLED=false` |
| Kill switch | `AEGIS_RUNTIME_MODE=ai_disabled` |
| Offline pack only | `AEGIS_RUNTIME_MODE=assessment` then `python -m aegis run --workflow batch --id NCB204-B24071` |

Workflow runbooks when inference is unavailable: `docs/runbooks/`. Incident procedure: `ops/runbooks/incident.md`.

## Stop

Interrupt the `serve` process. Working state is in-process plus the evidence chain. Export before tearing down a machine you care about: `python -m aegis evidence-export`.

## Identities and data

Identities come from `tests/fixtures/synthetic/data/users_entitlements.csv`. Catalog ids come from `packages/config/catalog.py`. Do not invent either.
