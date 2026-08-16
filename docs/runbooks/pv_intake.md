# Manual path — PV intake

**Inject:** INJ-082 (AI-disabled continuity).  
**Obligation:** clocks, duplicate candidates, and listedness remain in the pack. The console never confirms a safety signal.

Use this runbook immediately when `max_ai_outage_hours` is 0, or when inference is off.

1. Produce the pack: `python -m aegis run --workflow pv --id PV-1001`.
2. Or open `/workflows/pv/PV-1001` with the model off.
3. Retain every source clock, listedness row, and duplicate candidate without pooling or expectedness.
4. Sensitive segments appear only for an entitled role. An unentitled role sees them withheld.
5. Do not confirm a safety signal. Escalate incomplete cases to the entitled reviewer.
6. Reconcile work recorded during the outage before any later AI-assisted run.
