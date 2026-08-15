# ADR-005: Non-execution and deny-list

- Status: Accepted
- Date: 2026-08-13

## Decision

Every pack has `execution_status: not_executed`. The deny-list grader scans rendered strings at any depth. The list may only grow; shrinking fails the baseline-hash check.

## Consequences

Prohibited language such as "approved for release" in nested free text is a contract failure, not a review comment.
