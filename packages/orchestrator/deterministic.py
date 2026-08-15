"""Stdlib deterministic runner. Authoritative assessed path (ADR-008)."""

from __future__ import annotations

from typing import Any, Callable

from packages.advice.resolve import resolve_inference
from packages.config.agents import tool_allowed
from packages.config.runtime import inference_allowed
from packages.contracts.resolve import resolve_contract
from packages.contracts.validator import validate
from packages.domain.batch import iter_records
from packages.domain.orchestration import (
    budget_stop_abstention,
    retry_exhausted_abstention,
    undeclared_budget_abstention,
)
from packages.evidence_store.writer import persist_llm, persist_run
from packages.finops.budgets import admit_budgets, exhausted
from packages.finops.wallet import admit as wallet_admit
from packages.graph.builder import build_projection, graph_summary
from packages.kernel.audit import audit_events
from packages.kernel.checkpoint import persist_step_checkpoint, record_agency_attempt
from packages.kernel.lifecycle import start_request
from packages.kernel.packs import advisory_pack, batch_pack, pv_pack, supply_pack
from packages.orchestrator.graph import DECLARED_STEPS, role_for_step


class StepFailure(Exception):
    """Injected step failure for retry-bound tests. Not a domain classification."""


class StdlibOrchestrator:
    def __init__(self, *, fail_hook: Callable[[str], None] | None = None, runner: str = "stdlib") -> None:
        self._fail_hook = fail_hook
        self.runner = runner
        self._graph = None
        self._request: dict[str, Any] = {}
        self._fixture: dict[str, Any] = {}
        self._started: dict[str, Any] = {}
        self._budgets: dict[str, Any] = {}
        self._counters: dict[str, int] = {}
        self._record_ids: list[str] = []
        self._source_hashes: list[str] = []
        self._scenario_id = ""
        self._workflow = ""

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        state = self.begin(request)
        if state.get("stopped"):
            return state["pack"]
        for step in DECLARED_STEPS:
            state = self.advance(state, step)
            if state.get("stopped"):
                return state["pack"]
        return self.finish(state)

    def begin(self, request: dict[str, Any]) -> dict[str, Any]:
        self._graph = None
        self._request = dict(request)
        fixture = dict(request.get("fixture") or {})
        self._fixture = fixture
        context = dict(fixture.get("authorized_context") or {})
        scenario = dict(fixture.get("scenario") or {})
        self._scenario_id = str(scenario.get("id") or "UNSET")
        self._workflow = str(request.get("workflow") or scenario.get("workflow") or "")
        started = start_request(context, scenario_id=self._scenario_id)
        self._started = started
        request_id = str(started["request_id"])
        budgets = admit_budgets(request.get("budgets") if "budgets" in request else None)
        if budgets is None:
            return {
                "pack": _partial_pack(
                    fixture,
                    started,
                    [undeclared_budget_abstention(self._scenario_id).as_dict()],
                    gate_outcome="abstained",
                    runner=self.runner,
                ),
                "stopped": True,
                "steps_done": [],
            }
        if not wallet_admit():
            return {
                "pack": _partial_pack(
                    fixture,
                    started,
                    [budget_stop_abstention(self._scenario_id, "wallet").as_dict()],
                    gate_outcome="abstained",
                    runner=self.runner,
                ),
                "stopped": True,
                "steps_done": [],
            }
        self._budgets = budgets
        proposed = [str(item) for item in (request.get("proposed_steps") or [])]
        extras = [step for step in proposed if step not in DECLARED_STEPS]
        for step in extras:
            record_agency_attempt(request_id, step)
        for tool in [str(item) for item in (request.get("proposed_tools") or [])]:
            owner = role_for_step("retrieve", self._workflow)
            if owner.startswith("AG-") and not tool_allowed(owner, tool):
                record_agency_attempt(request_id, tool)
        self._counters = {
            "steps": 0,
            "tokens": int(request.get("token_usage") or 0),
            "tool_calls": 0,
            "retries": 0,
        }
        self._record_ids = _reference_ids(fixture)
        self._source_hashes = _source_hashes(fixture)
        return {"pack": None, "stopped": False, "steps_done": []}

    def advance(self, state: dict[str, Any], step: str) -> dict[str, Any]:
        if state.get("stopped"):
            return state
        steps_done = list(state.get("steps_done") or [])
        pack = state.get("pack")
        persist_step_checkpoint(
            {
                "request_id": self._started.get("request_id"),
                "step": step,
                "role": role_for_step(step, self._workflow),
                "durability": "sync",
                "record_ids": self._record_ids,
                "source_hashes": self._source_hashes,
                "counters": dict(self._counters),
                "input_hash": self._started.get("request_id"),
            }
        )
        self._counters["steps"] += 1
        reason = exhausted(self._counters, self._budgets)
        if reason:
            return {
                "pack": _partial_pack(
                    self._fixture,
                    self._started,
                    [budget_stop_abstention(self._scenario_id, reason).as_dict()],
                    gate_outcome="partial_coverage",
                    steps=steps_done,
                    runner=self.runner,
                ),
                "stopped": True,
                "steps_done": steps_done,
            }
        while True:
            try:
                if self._fail_hook is not None:
                    self._fail_hook(step)
                pack = self._execute(step, self._fixture, self._request, pack)
                break
            except StepFailure:
                self._counters["retries"] += 1
                if self._counters["retries"] > int(self._budgets["max_retries"]):
                    return {
                        "pack": _partial_pack(
                            self._fixture,
                            self._started,
                            [retry_exhausted_abstention(self._scenario_id, step).as_dict()],
                            gate_outcome="partial_coverage",
                            steps=steps_done,
                            runner=self.runner,
                        ),
                        "stopped": True,
                        "steps_done": steps_done,
                    }
        steps_done.append(step)
        return {"pack": pack, "stopped": False, "steps_done": steps_done}

    def finish(self, state: dict[str, Any]) -> dict[str, Any]:
        pack = state.get("pack")
        assert pack is not None
        steps_done = list(state.get("steps_done") or [])
        review = dict(pack.get("human_review") or {})
        review["orchestration"] = {
            "runner": self.runner,
            "steps": list(DECLARED_STEPS),
            "steps_completed": steps_done,
            "step_roles": [role_for_step(step, self._workflow) for step in steps_done],
            "budgets": self._budgets,
            "counters": self._counters,
        }
        updated = dict(pack)
        updated["human_review"] = review
        return updated

    def _execute(
        self,
        step: str,
        fixture: dict[str, Any],
        request: dict[str, Any],
        pack: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        if step == "project_graph":
            as_of = str((fixture.get("authorized_context") or {}).get("as_of") or "")
            self._graph = build_projection(as_of=as_of)
            return pack
        if step == "package":
            workflow = str(request.get("workflow") or (fixture.get("scenario") or {}).get("workflow") or "")
            entity_id = str(request.get("entity_id") or "")
            if workflow in {"batch", "batch_evidence"}:
                built = batch_pack(fixture, batch_id=entity_id or "NCB204-B24071")
            elif workflow in {"pv", "pv_intake"}:
                built = pv_pack(fixture, case_ids=[entity_id or "PV-1001"])
            elif workflow in {"supply", "supply_options"}:
                built = supply_pack(fixture, event_id=entity_id or "SH-901")
            else:
                built = advisory_pack(fixture)
            built = _attach_graph_summary(built, self._graph, entity_id)
            return _maybe_annotate(built)
        if step == "validate_emit" and pack is not None:
            contract = str(fixture.get("response_contract") or "advisory_nonexecuting")
            validate(pack, resolve_contract(contract))
        return pack


def _attach_graph_summary(pack: dict[str, Any], graph: Any, entity_id: str) -> dict[str, Any]:
    if graph is None:
        return pack
    review = dict(pack.get("human_review") or {})
    review["graph_projection"] = graph_summary(
        graph,
        entity_id,
        as_of=str(pack.get("as_of") or ""),
    )
    updated = dict(pack)
    updated["human_review"] = review
    return updated


def _maybe_annotate(pack: dict[str, Any]) -> dict[str, Any]:
    if not inference_allowed():
        return pack
    result = resolve_inference().generate(pack)
    persist_llm(str(pack.get("request_id") or ""), result)
    advice = result.get("annotations")
    if not advice:
        return pack
    review = dict(pack.get("human_review") or {})
    review["annotations"] = advice
    updated = dict(pack)
    updated["human_review"] = review
    return updated


def _reference_ids(fixture: dict[str, Any]) -> list[str]:
    found: list[str] = []
    for _source, record in iter_records(fixture):
        for key in ("run_id", "checkpoint", "batch_id", "case_id", "event_id", "result_id"):
            value = record.get(key)
            if value:
                found.append(str(value))
                break
    return found


def _source_hashes(fixture: dict[str, Any]) -> list[str]:
    hashes: list[str] = []
    for blob in fixture.get("evidence") or []:
        digest = blob.get("sha256")
        if digest:
            hashes.append(str(digest))
    return hashes


def _partial_pack(
    fixture: dict[str, Any],
    started: dict[str, Any],
    abstentions: list[dict[str, Any]],
    *,
    gate_outcome: str,
    steps: list[str] | None = None,
    runner: str = "stdlib",
) -> dict[str, Any]:
    context = dict(fixture.get("authorized_context") or {})
    scenario = dict(fixture.get("scenario") or {})
    workflow = str(scenario.get("workflow") or "agent")
    if workflow not in {
        "security",
        "reliability",
        "privacy",
        "integration",
        "agent",
        "finops",
        "clinical",
        "regulatory",
    }:
        workflow = "agent"
    pack = {
        "request_id": started["request_id"],
        "scenario_id": str(scenario.get("id") or "UNSET"),
        "workflow": workflow,
        "as_of": str(context.get("as_of") or ""),
        "authorization": {
            "user": str(context.get("user") or ""),
            "purpose": str(context.get("purpose") or ""),
            "checked_at": str(context.get("as_of") or ""),
            "decision": "allow",
        },
        "evidence": [],
        "contradictions": [],
        "gaps": [],
        "abstentions": abstentions,
        "findings": [],
        "required_reviews": [],
        "human_review": {
            "orchestration": {
                "runner": runner,
                "steps": list(DECLARED_STEPS),
                "steps_completed": list(steps or []),
                "stopped": True,
            }
        },
        "execution_status": "not_executed",
        "gate_outcome": gate_outcome,
        "no_side_effects": True,
        "audit": {"hash_scope": "source_artifact"},
    }
    validate(pack, resolve_contract("advisory_nonexecuting"))
    persist_run(pack, fixture, audit_tail=audit_events()[-8:])
    return pack
