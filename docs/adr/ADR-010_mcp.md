# ADR-010: MCP is optional and read-only

- Status: Accepted
- Date: 2026-08-13

## Decision

Runtime MCP is **off by default**. A read-only client may be enabled in `ui` / `cloud` against an allow-list. An AEGIS MCP *server* is demo-only and read-only. Tool manifests are signed and verified at execution time (TASK-023). A poisoned manifest is rejected.

## Consequences

`packages/` cannot import `mcp`. Cursor `mcp.json` is TASK-001b, not a runtime dependency of `assessment`.
