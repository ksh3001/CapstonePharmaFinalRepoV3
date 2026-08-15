"""Static declared step graph. The model never chooses the next step (BR-049)."""

from __future__ import annotations

DECLARED_STEPS = (
    "admit",
    "plan",
    "retrieve",
    "project_graph",
    "reconcile",
    "annotate",
    "approve",
    "package",
    "validate_emit",
)

STEP_ROLES = {
    "admit": "kernel",
    "plan": "AG-1",
    "retrieve": "AG-2",
    "project_graph": "AG-2",
    "reconcile": "workflow",
    "annotate": "workflow",
    "approve": "AG-1",
    "package": "AG-6",
    "validate_emit": "kernel",
}

WORKFLOW_AGENTS = {
    "batch": "AG-3",
    "batch_evidence": "AG-3",
    "pv": "AG-4",
    "pv_intake": "AG-4",
    "supply": "AG-5",
    "supply_options": "AG-5",
}


def role_for_step(step: str, workflow: str = "") -> str:
    role = STEP_ROLES.get(step) or "kernel"
    if role != "workflow":
        return role
    return WORKFLOW_AGENTS.get(workflow, "AG-1")
