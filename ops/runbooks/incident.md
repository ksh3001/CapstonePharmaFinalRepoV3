# Incident runbook

Use this when a gate, kill switch, residency denial, poisoned tool, or suspected posture break occurs.

1. Leave inference off or turn `AEGIS_LLM_ENABLED=false` / `AEGIS_RUNTIME_MODE=ai_disabled`.
2. Do not delete evidence. Export the chain (`python -m aegis evidence-export`) and keep the process logs.
3. Record the event with `templates/incident-record.md` under `evidence/incidents/`.
4. If a write tool, missing acknowledge gate, unpinned model, off-policy region, shrunk deny-list, or loosened threshold is involved, treat the event as: EU AI Act applicability claim invalidated — re-run artefact 19.
5. Restore from a known-good commit. Re-run `python -m aegis test` before serving again.

The kill switch is a runtime control. This runbook is the human procedure around it.
