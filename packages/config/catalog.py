"""Selectable synthetic entities for console, CLI, and API routing.

Presentation layers must not invent identifiers. Every picker, search hit,
status row, and CLI fixture lookup comes from this table.
"""

from __future__ import annotations

from typing import NamedTuple


class Entity(NamedTuple):
    workflow: str
    entity_id: str
    fixture: str
    label: str
    product: str
    picker: bool = True
    board: bool = True
    search_primary: bool = True


WORKFLOWS = ("batch", "pv", "supply")
TITLES = {
    "batch": "Batch evidence",
    "pv": "PV intake",
    "supply": "Supply / cold-chain",
}

# One row per identity a reviewer can open. Shared fixtures (PV cluster, SH-901/902)
# keep picker=True so every id is selectable; board=True only on the first of each
# fixture so Status / Home / Contradictions load each pack once.
ENTITIES: tuple[Entity, ...] = (
    Entity("batch", "NCB204-B24071", "PUB-01.json", "NCB-204 quality hold", "NCB-204"),
    Entity("batch", "NCS310-S26033", "PUB-02.json", "NCS-310 pending review", "NCS-310"),
    Entity("pv", "PV-1001", "PUB-04.json", "ICSR PV-1001 (duplicate cluster)", "NCB-204"),
    Entity("pv", "PV-1009", "PUB-04.json", "ICSR PV-1009 (duplicate cluster)", "NCB-204", board=False),
    Entity("pv", "PV-1014", "PUB-04.json", "ICSR PV-1014 (duplicate cluster)", "NCB-204", board=False),
    Entity("pv", "SM-77", "PUB-05.json", "Social-listening signal SM-77", "NCB-204"),
    Entity("pv", "NCB-204", "PUB-06.json", "NCB-204 listedness across regions", "NCB-204"),
    Entity("supply", "SH-901", "PUB-08.json", "SH-901 cold-chain dispute", "NCB-204"),
    Entity("supply", "SH-902", "PUB-08.json", "SH-902 customs hold", "NCS-310", board=False),
    Entity("supply", "NCB-204-shortage", "PUB-07.json", "NCB-204 shortage options", "NCB-204"),
    Entity(
        "supply",
        "NCB-204",
        "PUB-07.json",
        "NCB-204 shortage options",
        "NCB-204",
        board=False,
        search_primary=False,
    ),
    Entity("batch", "PUB-03", "PUB-03.json", "PUB-03 fail-closed batch", "NCB-204", picker=False, board=False),
    Entity("pv", "PUB-04", "PUB-04.json", "PUB-04", "NCB-204", picker=False, board=False),
    Entity("pv", "PUB-05", "PUB-05.json", "PUB-05", "NCB-204", picker=False, board=False),
    Entity("pv", "PUB-06", "PUB-06.json", "PUB-06", "NCB-204", picker=False, board=False),
    Entity("supply", "PUB-07", "PUB-07.json", "PUB-07", "NCB-204", picker=False, board=False),
    Entity("supply", "PUB-08", "PUB-08.json", "PUB-08", "NCB-204", picker=False, board=False),
)


def entities_for(workflow: str, *, picker_only: bool = False) -> tuple[Entity, ...]:
    rows = [item for item in ENTITIES if item.workflow == workflow]
    if picker_only:
        rows = [item for item in rows if item.picker]
    return tuple(rows)


def picker_entities(workflow: str) -> tuple[Entity, ...]:
    return entities_for(workflow, picker_only=True)


def board_entities() -> tuple[Entity, ...]:
    return tuple(item for item in ENTITIES if item.board)


def default_entity(workflow: str) -> str:
    for item in ENTITIES:
        if item.workflow == workflow and item.picker:
            return item.entity_id
    raise KeyError(workflow)


def defaults() -> dict[str, str]:
    return {workflow: default_entity(workflow) for workflow in WORKFLOWS}


def lookup(workflow: str, entity_id: str) -> Entity | None:
    wanted = (entity_id or "").strip()
    for item in ENTITIES:
        if item.workflow == workflow and item.entity_id == wanted:
            return item
    return None


def product_for(workflow: str, entity_id: str) -> str:
    found = lookup(workflow, entity_id)
    return found.product if found is not None else ""


def fixture_for(workflow: str, entity_id: str) -> str:
    found = lookup(workflow, entity_id)
    if found is not None:
        return found.fixture
    wanted = (entity_id or "").strip().upper()
    if workflow == "pv":
        return "PUB-04.json"
    if workflow == "supply":
        return "PUB-08.json" if wanted.startswith("SH-") else "PUB-07.json"
    return "PUB-01.json"


def href_for(workflow: str, entity_id: str) -> str:
    return f"/workflows/{workflow}/{entity_id}"


def find_in_text(raw: str) -> Entity | None:
    """Return the longest catalog id mentioned in free text, or None."""
    upper = (raw or "").upper()
    if not upper:
        return None
    hits = [item for item in ENTITIES if item.entity_id.upper() in upper]
    if not hits:
        return None
    hits.sort(key=lambda item: (len(item.entity_id), item.search_primary), reverse=True)
    return hits[0]


def search_href(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return href_for("batch", default_entity("batch"))
    upper = text.upper()
    matches = [item for item in ENTITIES if item.entity_id.upper() == upper]
    if matches:
        primary = next((item for item in matches if item.search_primary), matches[0])
        return href_for(primary.workflow, primary.entity_id)
    if upper.startswith("PV") or upper.startswith("SM"):
        return href_for("pv", text)
    if upper.startswith("SH"):
        return href_for("supply", text)
    return href_for("batch", text)
