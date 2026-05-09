from __future__ import annotations

import json
import re

import httpx

from app.core.config import settings


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _rules_score(request: str) -> str:
    """
    Heuristic scoring based on intent/urgency.
    Returns: High | Medium | Low
    """
    r = _normalize(request)
    if not r:
        return "Low"

    high_signals = [
        "urgent",
        "asap",
        "today",
        "now",
        "call me",
        "budget",
        "quote",
        "pricing",
        "proposal",
        "contract",
        "ready",
        "buy",
        "purchase",
        "order",
        "book",
        "appointment",
        "meeting",
        "demo",
        "trial",
        "שיחה",
        "דחוף",
        "הצעת מחיר",
        "מחיר",
        "תמחור",
        "לקנות",
        "לרכוש",
        "לקבוע",
        "הדגמה",
    ]
    medium_signals = [
        "interested",
        "details",
        "info",
        "information",
        "how much",
        "cost",
        "options",
        "availability",
        "schedule",
        "מעניין",
        "פרטים",
        "מידע",
        "אפשרויות",
        "זמינות",
        "עלות",
        "כמה עולה",
    ]

    if any(k in r for k in high_signals):
        return "High"
    if any(k in r for k in medium_signals):
        return "Medium"

    # Longer, specific requests tend to be warmer than vague ones.
    if len(r) >= 35:
        return "Medium"
    return "Low"


def score_lead(*, request: str) -> str:
    """
    Best-effort AI scoring.
    - If AI_PROVIDER=openai and OPENAI_API_KEY is set, uses OpenAI.
    - Otherwise falls back to rules scoring.
    """
    provider = (settings.ai_provider or "rules").lower()
    if provider != "openai" or not settings.openai_api_key.strip():
        return _rules_score(request)

    sys = (
        "You are a sales assistant. Classify the lead priority based ONLY on the request text. "
        "Return exactly one token: High, Medium, or Low."
    )
    user = f"Request: {request or ''}"
    payload = {
        "model": settings.openai_model.strip() or "gpt-4.1-mini",
        "messages": [{"role": "system", "content": sys}, {"role": "user", "content": user}],
        "temperature": 0.0,
        "max_tokens": 3,
    }
    headers = {"Authorization": f"Bearer {settings.openai_api_key.strip()}", "Content-Type": "application/json"}
    try:
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
        if content in ("High", "Medium", "Low"):
            return content
        return _rules_score(request)
    except Exception:
        return _rules_score(request)

