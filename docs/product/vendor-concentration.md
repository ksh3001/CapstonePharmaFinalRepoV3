# Vendor concentration

**Inject:** INJ-078 (vendor concentration).  
**Obligation:** single-vendor concentration is reported wherever cost is reported, with the exit cost and the alternative on record. A port exists so the vendor can be removed.

## The risk

Azure OpenAI, optional Redis, optional MCP, and optional Blob are one-vendor concentrations if they become the only path to a pack. Assessment mode exists so they are not.

## What the product does

- Every third-party capability sits behind a port (AP-6).
- `assessment` and `ai_disabled` produce a schema-valid pack with those adapters uninstalled (AC-FR009-12, AC-FR014-12).
- FinOps reporting names concentration and the recorded alternative (AC-FR007-10a).
- `specs/poc_vs_production.md` labels cloud adapters **Demonstrator**, not production-intent.

## Exit

See `docs/operations/vendor-exit.md`. The alternative on record for inference is the no-AI baseline (`docs/product/no-ai-baseline.md`).
