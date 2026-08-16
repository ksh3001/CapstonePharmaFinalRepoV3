"""Demo console passwords. Fixture walkthrough only — not Entra ID, not production auth."""

from __future__ import annotations

import hmac

# Usernames must already exist and be assumable in users_entitlements.csv.
DEMO_PASSWORDS: dict[str, str] = {
    "qp_eu_1": "aegis-demo",
}


def demo_password_for(user: str) -> str | None:
    return DEMO_PASSWORDS.get((user or "").strip())


def verify_demo_password(user: str, password: str) -> bool:
    expected = demo_password_for(user)
    if expected is None:
        return False
    return hmac.compare_digest(expected, password or "")


def demo_credential_hint() -> str:
    """Shown on the login page so the walkthrough can proceed without a secrets vault."""
    parts = [f"{user} / {password}" for user, password in sorted(DEMO_PASSWORDS.items())]
    return "; ".join(parts)
