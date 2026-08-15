# AEGIS

Advisory, human-in-the-loop evidence console for three workflows: **batch evidence**, **PV intake**, and **supply / cold-chain**.

Deterministic engines in `packages/domain` produce the pack. Agents sequence work; they do not decide. Azure OpenAI, when enabled, writes labelled narrative only. A qualified human decides outside this system.

This is a capstone / challenge build with synthetic fixtures. It is not a production GxP system of record and it is not EU AI Act or ISO/IEC 42001 certified. Intended use: `docs/product/intended-use.md`.

## What you need

| Requirement | Notes |
|---|---|
| CPython **≥ 3.11 and < 3.14** | Verified by `python -m aegis setup` |
| Git clone of this repo | Synthetic fixtures are already in `tests/fixtures/synthetic/` |
| Optional: `pip install -r requirements-ui.txt` | FastAPI + Jinja + uvicorn for the HTML console |
| Optional: Azure OpenAI settings | Only for `advisory` mode with the model on |

No Node, no `npm`, no database. Assessment mode installs nothing.

The sibling FDE challenge package is **not** required to run or test. If it is present next to this repo (or `AEGIS_CHALLENGE_ROOT` points at it), setup copies from it; otherwise setup uses the committed copy set.

Do not commit `.env`. Copy `.env.example` and keep secrets out of git.

## Run the console (usual path)

From the repo root:

```text
python -m pip install -r requirements-ui.txt
python -m aegis setup
python -m aegis serve --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/**

Without the UI extras, `serve` still starts a stdlib HTML console. The FastAPI install is what you want for the full screens.

### First minutes in the UI

1. Assume an identity in the header picker (default is the first assumable fixture user, typically `qp_eu_1` — EU Qualified Person).
2. Click the **question-mark** icon (top right) for the user guide with screenshots of every page.
3. Open a catalog id from the left rail or the dashboard directory.

| Workflow | Example id | What you will see |
|---|---|---|
| Batch | `NCB204-B24071` | NCB-204 quality hold pack |
| Batch | `NCS310-S26033` | NCS-310 pending review |
| PV | `PV-1001` | ICSR duplicate cluster |
| PV | `SM-77` | Social-listening signal |
| Supply | `SH-901` | Cold-chain dispute |
| Supply | `NCB-204-shortage` | Shortage options (draft only) |

Search in the header accepts those ids. Pack chat (bottom right) answers status or graph questions for a catalog id. It will not dispose a batch or confirm a signal.

Acknowledge stays unavailable until every **critical** evidence row is opened. Acknowledge and contest are workflow events, not signatures.

## Run a pack from the CLI (no browser)

```text
python -m aegis setup
python -m aegis run --workflow batch --id NCB204-B24071
python -m aegis run --workflow pv --id PV-1001
python -m aegis run --workflow supply --id SH-901
```

Output is canonical JSON on stdout.

## Runtime modes

Set `AEGIS_RUNTIME_MODE`. `AEGIS_LLM_ENABLED=false` turns the model off in every mode, including `advisory`.

| Mode | Meaning |
|---|---|
| `assessment` (**default for grading**) | Stdlib only. No installs, no network, no model. CLI → JSON packs. |
| `ai_disabled` | Kill switch. Same regulated fields as `assessment`. |
| `advisory` | Azure OpenAI narrative only, behind `InferencePort`. |
| `ui` | FastAPI console. Model off unless cassette replay. |
| `cloud` | Demo adapters (Redis, MCP, Blob). Never required to grade. |

Local console with a model: copy `.env.example` to `.env` and fill Azure names. Local demo often uses:

```text
AEGIS_RUNTIME_MODE=advisory
AEGIS_LLM_ENABLED=true
```

plus `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` (or managed identity), `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_MODEL_VERSION`, and `AZURE_OPENAI_REGION`. Pin the model version. Do not use `latest` / `current` / `alias`.

To run the console **without** a model:

```text
AEGIS_RUNTIME_MODE=ui
AEGIS_LLM_ENABLED=false
python -m aegis serve --port 8000
```

On Windows PowerShell:

```powershell
$env:AEGIS_RUNTIME_MODE="ui"
$env:AEGIS_LLM_ENABLED="false"
python -m aegis serve --port 8000
```

`serve` loads `.env` when present (`packages/config/envfile.py`). Empty values in `.env.example` are names only.

## Environment variables

| Name | Required to run? | Purpose |
|---|---|---|
| `AEGIS_RUNTIME_MODE` | No (defaults to `assessment`) | Mode table above |
| `AEGIS_LLM_ENABLED` | No (defaults to off) | Master inference switch |
| `AEGIS_ALLOW_KEY_AUTH` | No | Set to `dev` only for local key auth; never for grading |
| `AEGIS_CHALLENGE_ROOT` | No | Path to the sibling FDE package if you have it |
| `AZURE_OPENAI_ENDPOINT` | Only if the model is on | Azure OpenAI resource URL |
| `AZURE_OPENAI_API_KEY` | Only if using key auth | Do not commit |
| `AZURE_OPENAI_DEPLOYMENT` | Only if the model is on | Must match `compliance/eu-ai-act/model-registry.json` |
| `AZURE_OPENAI_MODEL_VERSION` | Only if the model is on | Pinned version, same registry |
| `AZURE_OPENAI_API_VERSION` | Only if the model is on | Azure API version |
| `AZURE_OPENAI_REGION` | Only if the model is on | Must be in `compliance/eu-ai-act/residency-policy.json` |
| `AZURE_CLIENT_ID` | No | Managed identity, if used |
| `GENERATOR_DEPLOYMENT` | No | Mapped onto `AZURE_OPENAI_DEPLOYMENT` if that is empty |

## Other commands

```text
python -m aegis setup              # copy-set + structure manifest + quality gates
python -m aegis test               # full unittest suite (tests/ + quality/static-analysis/)
python -m aegis evaluate           # eval graders
python -m aegis reset              # clear replay / working state
python -m aegis evidence-export    # write out/evidence-export.json
python -m aegis evidence --request-id REQ-…
python -m aegis verify-evidence
python -m aegis serve --port 8000
python scripts/ci.py               # setup + full test + evaluate (same as GitHub CI)
```

## Tests and CI

`python -m aegis test` is the gate. GitHub Actions (`.github/workflows/ci.yml`) runs that suite on 3.11 and 3.12, plus a UI job with `requirements-ui.txt`. Deploy (`.github/workflows/deploy-azure.yml`) waits for CI on `main`.

Azure Web App steps: `docs/operations/azure-webapp.md`.

## Documentation (FDE layering)

One question per file. Specs in `specs/` win if a doc and a spec disagree.

| Read this | When |
|---|---|
| `docs/README.md` | Documentation register — start here |
| `docs/product/intended-use.md` | What the product does and must never decide |
| `docs/architecture/overview.md` | Where code belongs |
| [C4 architecture (HTML)](docs/architecture/aegis-architecture.html) | Interactive system diagram |
| `docs/engineering/developer-guide.md` | How to change the repo without breaking a gate |
| `docs/operations/operator-guide.md` | Start, degrade, stop |
| `docs/quality/release-bar.md` | What must be green |
| `docs/security/posture.md` | Default security posture |
| `docs/compliance/eu-ai-act-iso-42001-status.md` | Checked vs certified |
| `CONTRIBUTING.md` | Hard rules for a pull request |

Workflow runbooks (model off): `docs/runbooks/`. ADRs: `docs/adr/`. Interactive C4 diagram: [docs/architecture/aegis-architecture.html](docs/architecture/aegis-architecture.html).

## Layout

| Path | Role |
|---|---|
| `aegis/` | CLI (`python -m aegis`) |
| `packages/` | Stdlib core. No third-party imports. |
| `services/api/` | JSON handlers + HTML console; optional FastAPI |
| `apps/web/` | Jinja templates, `aegis.css`, vendored HTMX |
| `tests/fixtures/synthetic/` | Hash-verified copy set used at runtime |
| `specs/` | Authoritative product specs |
| `compliance/` | Control map and tripwires |
| `docs/product/intended-use.md` | What the product does and does not do |
| `docs/compliance/eu-ai-act-iso-42001-status.md` | Compliance posture (not a certificate) |
| `REPO_MAP.md` | Full tree |

`STRUCTURE_MANIFEST.json` is generated. Do not hand-edit it.

## What this repository is not

- Not a batch-disposition, PV-decision, eligibility, allocation, or recall system
- Not a product graph stored in Cosmos DB
- Not a Node / Next.js application
- Challenge evidence in the sibling FDE package is never modified here
