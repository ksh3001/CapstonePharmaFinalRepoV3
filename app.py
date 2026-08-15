"""Azure App Service / Oryx ASGI entry. Assessment does not import this module."""

from __future__ import annotations

from services.api.fastapi_app import create_app
from services.integration.azure.openai import configure_inference

configure_inference(override=True)
app = create_app()
