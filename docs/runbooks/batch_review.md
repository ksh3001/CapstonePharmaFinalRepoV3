# Manual path — batch evidence review

**Inject:** INJ-082 (AI-disabled continuity).  
**Obligation:** a schema-valid batch pack remains reviewable with inference off. The reviewer does not infer a disposition from the pack.

Use this runbook when inference is unavailable or `AEGIS_RUNTIME_MODE` is `assessment` / `ai_disabled`.

1. Produce the pack: `python -m aegis run --workflow batch --id NCB204-B24071`.
2. Or open `/workflows/batch/NCB204-B24071` on a console started with the model off.
3. Read findings, contradictions, gaps, and abstentions with equal prominence. Do not infer a disposition.
4. Open every critical evidence item before recording acknowledgement.
5. Record reviewer identity, time, and the action taken on Status. That note is stored on the evidence chain.
6. Any regulated action happens in a system of record outside AEGIS.

Console user guide: question-mark icon in the header.
