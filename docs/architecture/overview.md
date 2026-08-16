# Architecture overview

**Question this file answers:** where code belongs, and which process is the product.

## One process

AEGIS is one Python process. The CLI (`python -m aegis`), the stdlib HTTP console, and optional FastAPI (`app.py`) call the same handlers. There is no separate Node UI and no message bus required to grade.

Interactive C4: `docs/architecture/aegis-architecture.html` (data: `aegis-architecture.json`).

## Layers

| Layer | Path | May import |
|---|---|---|
| Contracts, config | `packages/contracts`, `packages/config` | Stdlib only |
| Domain engines | `packages/domain` | Core packages. Only place `Contradiction`, `Gap`, `Abstention` are constructed |
| Kernel | `packages/kernel` | Core packages. Only place `write_audit` is called |
| Orchestrator | `packages/orchestrator` | Sequences engines. Does not classify |
| API / console | `services/api` | Packages + optional FastAPI/Jinja |
| Adapters | `services/integration` | Third parties. `packages/` must not import these |
| Web assets | `apps/web` | Templates and vendored HTMX/CSS. No build step |

Principles: `specs/product/scope.md` §5 (AP-1…AP-12). Durable choices: `docs/adr/`.

## Modes

`assessment` is the graded path: stdlib, offline, inference off. `ui` adds FastAPI. `advisory` may call Azure OpenAI for labelled annotations only. `cloud` adapters are demonstrators (`specs/poc_vs_production.md`).

## What architecture forbids

- Domain logic in LangGraph nodes (R-10 / MR-5)
- A write tool that could dispose, move stock, or finalise PV
- Caching authorisation, consent, residency, or legal-hold (AP-9)
- Treating the knowledge-graph projection as a system of record (AP-8)
