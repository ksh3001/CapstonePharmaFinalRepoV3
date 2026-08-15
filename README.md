# AEGIS

Advisory, human-in-the-loop evidence reconciliation for three mandated workflows: batch evidence, PV intake, and supply / cold-chain. Deterministic engines in `packages/domain` are the source of truth. Agents sequence; they do not decide. Azure OpenAI is narrative only and is off in the default graded mode.

## Runtime modes

| Mode | Meaning |
|---|---|
| `assessment` (**default for grading**) | Python standard library only. No installs, no network, no model. CLI → JSON packs. |
| `ai_disabled` | Kill switch honoured. Same regulated fields as `assessment`. |
| `advisory` | Deployed default. Azure OpenAI narrative only, behind `InferencePort`. |
| `ui` | FastAPI + server-rendered console. Model off unless cassette replay. |
| `cloud` | Demo adapters (Redis, MCP, Blob WORM). Never required to grade. |

`AEGIS_RUNTIME_MODE` selects the mode. `AEGIS_LLM_ENABLED=false` is honoured in every mode, including `advisory`.

## Commands (zero installs in `assessment`)

```text
python -m aegis setup
python -m aegis run --workflow batch --id NCB204-B24071
python -m aegis serve --port 8000
python -m aegis test
python -m aegis evaluate
python -m aegis reset
python -m aegis evidence-export
```

Interpreter pin: CPython ≥ 3.11 and < 3.14.

Live console: `python -m aegis serve` then open `http://127.0.0.1:8000/`. Optional UI extras: `pip install -r requirements-ui.txt` (FastAPI + Jinja). Not required to grade.

## CI and Azure Web App

`python scripts/ci.py` is the platform-neutral pipeline (setup, gates, tests, evaluate). GitHub Actions (`.github/workflows/ci.yml`) runs it on 3.11 and 3.12. Pushes to `main` then deploy the FastAPI console to Azure App Service (`.github/workflows/deploy-azure.yml`). Provisioning and secrets: `docs/operations/azure-webapp.md`.

## What this repository is not

- Not a batch-disposition, PV-decision, eligibility, allocation, or recall system.
- Not a product graph stored in Cosmos DB.
- Not a Node / Next.js application.
- Challenge evidence lives in the sibling FDE package and is never modified here.

## Layout

See `REPO_MAP.md` and `STRUCTURE_MANIFEST.json` (generated; do not hand-edit).
