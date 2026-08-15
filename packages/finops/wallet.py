"""Cumulative wallet ceiling. Exhaustion refuses new runs (BR-062)."""

from __future__ import annotations

from decimal import Decimal

WALLET_CEILING = Decimal("1000000")
_SPENT = Decimal("0")


def reset_wallet() -> None:
    global _SPENT
    _SPENT = Decimal("0")


def record_spend(amount: Decimal | str | int) -> None:
    global _SPENT
    _SPENT += Decimal(str(amount))


def remaining() -> Decimal:
    return WALLET_CEILING - _SPENT


def admit() -> bool:
    return remaining() > 0


def spent() -> Decimal:
    return _SPENT
