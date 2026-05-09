from __future__ import annotations

import json

import httpx

from app.core.config import settings
from app.services.ai.base import AIProvider, AIResult


class OpenAIProvider(AIProvider):
    """
    Uses OpenAI Chat Completions via HTTPS. Kept dependency-light (httpx only).
    If not configured, callers should fall back to RulesAI.
    """

    def __init__(self) -> None:
        self._api_key = settings.openai_api_key.strip()
        self._model = settings.openai_model.strip() or "gpt-4.1-mini"

    def _configured(self) -> bool:
        return bool(self._api_key)

    def respond(self, message: str) -> AIResult:
        if not self._configured():
            return AIResult(reply="", confidence=0.0)

        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful business lead bot. "
                        "Answer succinctly, ask for contact details when needed, and stay polite."
                    ),
                },
                {"role": "user", "content": message},
            ],
            "temperature": 0.4,
        }

        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

        with httpx.Client(timeout=20.0) as client:
            r = client.post("https://api.openai.com/v1/chat/completions", headers=headers, content=json.dumps(payload))
            r.raise_for_status()
            data = r.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        return AIResult(reply=content or "אשמח לעזור — אפשר להשאיר שם וטלפון?", confidence=0.7)

