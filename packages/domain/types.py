"""Classification types. Literal construction outside this package fails the MR-5 gate."""

from __future__ import annotations

from typing import Any


class Contradiction:
    def __init__(self, topic: str, source: str, record_id: str, **extra: Any) -> None:
        self.topic = topic
        self.source = source
        self.record_id = record_id
        self.extra = extra

    def as_dict(self) -> dict[str, Any]:
        payload = {"topic": self.topic, "source": self.source, "record_id": self.record_id}
        payload.update(self.extra)
        return payload


class Gap:
    def __init__(self, gap_type: str, subject_id: str, **extra: Any) -> None:
        self.gap_type = gap_type
        self.subject_id = subject_id
        self.extra = extra

    def as_dict(self) -> dict[str, Any]:
        payload = {"gap_type": self.gap_type, "subject_id": self.subject_id}
        payload.update(self.extra)
        return payload


class Abstention:
    def __init__(self, reason_code: str, subject_id: str, **extra: Any) -> None:
        self.reason_code = reason_code
        self.subject_id = subject_id
        self.extra = extra

    def as_dict(self) -> dict[str, Any]:
        payload = {"reason_code": self.reason_code, "subject_id": self.subject_id}
        payload.update(self.extra)
        return payload
