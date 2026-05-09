from __future__ import annotations

from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.rules import RulesAI


def get_ai_provider() -> AIProvider:
    if settings.ai_provider.lower() == "openai":
        provider = OpenAIProvider()
        if getattr(provider, "_configured")():
            return provider
    return RulesAI()

