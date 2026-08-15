"""Checkpoint freshness bound. Changing this value requires an ADR (FR-006 §9)."""

from __future__ import annotations

# PUB-13 records AR-77 at 380 minutes, which must exceed this bound.
MAX_STATE_AGE_MINUTES = 60
CONFIG_STATUS = "FR-006 default; not a validated GxP limit"
