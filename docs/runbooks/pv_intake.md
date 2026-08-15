# Manual path — PV intake

Use this runbook immediately when `max_ai_outage_hours` is 0.

1. Open the schema-valid pack produced by `python -m aegis run --workflow pv`.
2. Retain every source clock, listedness row and duplicate candidate without pooling.
3. Do not confirm a safety signal. Escalate incomplete cases to the entitled reviewer.
4. Reconcile work recorded during the outage before any later AI-assisted run.
