"""Re-identification combination threshold. BR-047 is rule-based, not statistical k-anonymity."""

from __future__ import annotations

REIDENTIFICATION_K = 5
QUASI_IDENTIFIERS = ("disease", "variant", "country", "age", "postal_prefix")
CONFIG_STATUS = "BR-047 rule-based limitation; not a validated statistical model"
