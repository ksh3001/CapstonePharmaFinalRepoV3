"""Identity resolution. Four categorical tiers, no fuzzy matching (plan §29.1)."""

from __future__ import annotations

from packages.ontology.mappings import is_approved_status, load_idmp_mappings
from packages.ontology.types import Identifier, IdentityResult

ORG_NAMESPACES = ("CMO-IE", "BIOX", "NTG")
UNSCOPED = "UNSCOPED"


def parse_identifier(raw: str, *, scheme: str = "org_prefixed") -> Identifier:
    text = (raw or "").strip()
    for namespace in sorted(ORG_NAMESPACES, key=len, reverse=True):
        prefix = namespace + "|"
        if text.startswith(prefix):
            return Identifier(scheme=scheme, value=text[len(prefix) :], org_namespace=namespace)
    if "|" in text:
        namespace, value = text.split("|", 1)
        return Identifier(scheme=scheme, value=value, org_namespace=namespace or UNSCOPED)
    return Identifier(scheme="local", value=text, org_namespace=UNSCOPED)


def _complete(identifier: Identifier) -> bool:
    return bool(identifier.scheme and identifier.value and identifier.org_namespace not in {"", UNSCOPED})


def resolve_identity(
    left: Identifier,
    right: Identifier,
    *,
    mappings: tuple[dict[str, str], ...] | None = None,
    declared_edges: tuple[tuple[Identifier, Identifier], ...] = (),
) -> IdentityResult:
    if _complete(left) and left == right:
        return IdentityResult(verdict="SAME")
    if left.value == right.value and left.org_namespace != right.org_namespace:
        return IdentityResult(
            verdict="IdentityConflict",
            reason_code="cross_organisation_unmapped",
        )
    if not _complete(left) or not _complete(right):
        if left.value == right.value:
            return IdentityResult(verdict="IdentityConflict", reason_code="incomplete_namespace")
    rows = mappings if mappings is not None else load_idmp_mappings()
    for row in rows:
        local = row.get("local_product") or ""
        canonical = row.get("idmp_product") or ""
        pair = {local, canonical}
        if left.value in pair and right.value in pair and left.value != right.value:
            status = row.get("mapping_status") or ""
            mapping_id = f"{local}->{canonical}"
            if is_approved_status(status):
                return IdentityResult(verdict="SAME_BY_MAPPING", mapping_id=mapping_id)
            return IdentityResult(
                verdict="IdentityConflict",
                mapping_id=mapping_id,
                reason_code="mapping_not_approved",
            )
    for edge_left, edge_right in declared_edges:
        if {edge_left, edge_right} == {left, right}:
            return IdentityResult(verdict="RELATED")
    if left.value == right.value:
        return IdentityResult(verdict="IdentityConflict", reason_code="unmapped_identifier")
    return IdentityResult(verdict="IdentityConflict", reason_code="distinct")


def local_code_collision(left: Identifier, right: Identifier) -> bool:
    """BR-131: same local code, different issuing scope."""
    return left.value == right.value and left.org_namespace != right.org_namespace
