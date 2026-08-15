"""Resolve the inference port. Services may register an Azure adapter; packages never import it."""

from __future__ import annotations

from packages.advice.null import NullInference
from packages.advice.port import InferencePort

_PORT: InferencePort | None = None


def set_inference_port(port: InferencePort | None) -> None:
    global _PORT
    _PORT = port


def reset_inference_port() -> None:
    set_inference_port(None)


def resolve_inference() -> InferencePort:
    return _PORT if _PORT is not None else NullInference()
