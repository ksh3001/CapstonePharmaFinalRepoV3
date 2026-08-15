# ISO/IEC 42001 mapping

In-repo mapping only. Not a certificate.

| Clause / area | Where it lives |
|---|---|
| 4 Context and scope | `docs/governance/aims-scope.md` |
| 5 Leadership and AI policy | `docs/governance/ai-policy.md` |
| 6 Planning / impact | `docs/product/success-metrics.md`, `docs/product/business-case.md`, inject coverage |
| 7 Support / documented information | `docs/engineering/` (if present), `docs/adr/`, this folder |
| 8 Operation / lifecycle | `compliance/iso42001/change-class-baseline.json`, `tests/compliance/test_change_classes.py` |
| 9 Performance evaluation | `evals/thresholds.yaml`, `evals/run_evals.py` |
| 10 Improvement | `ops/runbooks/incident.md`, `templates/incident-record.md` |
| Annex A themes | Provenance and deny-list in `packages/`; tool allow-list in `services/integration/mcp/tools.py` |
