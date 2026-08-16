# Manual path — supply options

**Inject:** INJ-082 (AI-disabled continuity).  
**Obligation:** options stay draft. The pack does not move stock or start a recall.

Use this runbook when inference is unavailable.

1. Produce the pack: `python -m aegis run --workflow supply --id SH-901`.
2. Or open `/workflows/supply/SH-901` with the model off.
3. Treat every option as draft. Do not reserve, move stock, or ship.
4. Quality holds remain holds. Unqualified substitutes are described, not counted.
5. Approvals required where stock would move stay on the pack as text.
6. Reconcile outage-period drafts before any later AI-assisted run.
