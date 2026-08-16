# Retirement and evidence preservation

**Inject:** INJ-084 (retirement and evidence preservation).  
**Obligation:** prompts, model ids, thresholds, reviewer actions, and the audit trail remain inspectable after the product or a vendor is retired.

## What is retained

| Artefact | Where |
|---|---|
| Packs and reviewer events | Evidence chain (`python -m aegis evidence-export`) |
| Thresholds applied | `evals/thresholds.yaml` and `evals/thresholds.baseline.yaml` |
| Model pin | `compliance/eu-ai-act/model-registry.json` |
| System prompt | `services/integration/azure/openai.py` (versioned in git) |
| Deny-list | `packages/contracts/deny_list.json` plus baseline |
| Change records | `compliance/iso42001/change-class-baseline.json`, `evidence/ai-assisted-changes/` |
| Incident records | `evidence/incidents/` using `templates/incident-record.md` |

## How to read after exit

The store is readable with vendor integrations uninstalled (AC-FR014-12). The index rebuilds from the store (AC-FR014-13). Assessment mode is the read path.

## What is not retained as a regulated record

Packs are working drafts (`specs/product/scope.md`). Retirement preserves inspectability of *this product's* outputs. It does not create a GxP system of record.
