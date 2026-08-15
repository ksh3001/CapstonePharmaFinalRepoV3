"""Fixture entitlement identities for the demonstrator console.

Reads users_entitlements.csv live. Does not invent users. Does not cache (AP-9).
"""

from __future__ import annotations

import csv
from typing import NamedTuple

from packages.config.paths import synthetic_dir
from packages.config.roles import canonical_role, role_label


class SessionIdentity(NamedTuple):
    user: str
    role_spelling: str
    role_id: str | None
    iam_state: str
    gateway_state: str

    @property
    def assumable(self) -> bool:
        return self.iam_state == "active" and self.role_id is not None

    @property
    def display_role(self) -> str:
        if self.iam_state == "revoked":
            return "revoked"
        return role_label(self.role_id)

    @property
    def initials(self) -> str:
        compact = "".join(ch for ch in self.user if ch.isalnum())
        return (compact[:2] or "?").upper()


def _entitlements_path():
    return synthetic_dir() / "data" / "users_entitlements.csv"


def fixture_identities() -> tuple[SessionIdentity, ...]:
    path = _entitlements_path()
    if not path.is_file():
        return ()
    rows: list[SessionIdentity] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            user = str(raw.get("user") or "").strip()
            if not user:
                continue
            spelling = str(raw.get("role") or "").strip()
            rows.append(
                SessionIdentity(
                    user=user,
                    role_spelling=spelling,
                    role_id=canonical_role(spelling),
                    iam_state=str(raw.get("iam_state") or "").strip(),
                    gateway_state=str(raw.get("ai_gateway_state") or "").strip(),
                )
            )
    return tuple(rows)


def resolve_identity(user: str) -> SessionIdentity | None:
    wanted = (user or "").strip()
    if not wanted:
        return None
    for item in fixture_identities():
        if item.user == wanted:
            return item
    return None


def default_console_user() -> str:
    for item in fixture_identities():
        if item.assumable:
            return item.user
    return ""


def unresolved_identity(user: str) -> SessionIdentity:
    return SessionIdentity(
        user=(user or "").strip() or "unknown",
        role_spelling="",
        role_id=None,
        iam_state="",
        gateway_state="",
    )
