# ADR-007: Knowledge graph adoption

- Status: Accepted
- Date: 2026-08-13

## Decision

Artefact `08_KNOWLEDGE_GRAPH_DECISION.md` D-205 (no KG for the POC) is superseded. Triggers invoked: **X-1** (recall-scope recursion, INJ-058) and **X-2** (cross-domain inspection assembly, INJ-050).

The graph is an in-process projection rebuilt per run (plain-Python property graph). No database is the system of record. Cosmos DB for Gremlin is an optional `cloud`-mode adapter behind `GraphPort`, never required to grade.

T1–T5 parity from artefact 08 §3 must be proven before claiming KG value. Provenance columns migrate with the graph or the change is rejected (R-804).

## Consequences

`packages/graph` is stdlib. `networkx` / `rdflib` may exist only behind `GraphPort` in `services/integration/`.
