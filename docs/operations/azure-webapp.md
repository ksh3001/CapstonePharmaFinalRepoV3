# Deploy the AEGIS console to Azure Web App

The GitHub Actions workflow in `.github/workflows/deploy-azure.yml` zip-deploys this repository to a Linux Python 3.12 App Service after CI passes on `main`. Assessment still installs nothing; Azure installs `requirements.txt` (the UI extras) via Oryx.

## 1. Create the Web App

From a machine with Azure CLI signed in (`az login`):

```powershell
.\infra\environments\dev\provision.ps1 -AppName "<globally-unique-name>"
```

Or in the Azure Portal: create a **Web App**, Linux, **Python 3.12**, plan **B1** (Always On) or **F1** (free, cold start). Then set:

| Application setting | Value |
|---|---|
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |
| `WEBSITES_PORT` | `8000` |
| `AEGIS_RUNTIME_MODE` | `ui` |
| `AEGIS_LLM_ENABLED` | `false` |
| Startup command | `bash deploy/containers/startup.sh` |

Do not put API keys in the repository. Optional Azure OpenAI names (`AZURE_OPENAI_*`) go in App Service configuration only, and only if you switch the mode to `advisory` and set `AEGIS_LLM_ENABLED=true`.

## 2. Connect GitHub Actions

1. Download the publish profile:

   ```powershell
   az webapp deployment list-publishing-profiles --resource-group rg-aegis-dev --name "<app-name>" --xml
   ```

   Or Portal → Web App → **Get publish profile**.

2. In the GitHub repo **Settings → Secrets and variables → Actions**:
   - Secret `AZURE_WEBAPP_PUBLISH_PROFILE` = the XML publish profile
   - Variable `AZURE_WEBAPP_NAME` = the Web App name

3. Push to `main` (or run **Deploy Azure Web App** from the Actions tab).

The site URL is `https://<app-name>.azurewebsites.net/`. Liveness: `/healthz`.

## 3. What CI runs

`python scripts/ci.py` is the platform-neutral command. The workflow wraps it:

- Assessment on CPython 3.11 and 3.12 (zero pip installs): setup, quality-gate tests, evaluate
- One hostile `LANG` / `TZ` / `PYTHONHASHSEED` job
- One UI job that installs `requirements-ui.txt` and runs the FastAPI console tests

The full `python -m aegis test` suite still needs the sibling FDE challenge package (or `AEGIS_CHALLENGE_ROOT`). GitHub runners do not have that tree, so CI uses the committed copy set plus the gates.
