from __future__ import annotations

import json
import re

import httpx

from app.core.config import settings


_WS_RE = re.compile(r"\s+")


def _rules_summary(name: str, phone: str, request: str) -> str:
    n = (name or "").strip()
    p = (phone or "").strip()
    r = _WS_RE.sub(" ", (request or "").strip())
    r_short = (r[:140] + "…") if len(r) > 140 else r
    who = n or "New lead"
    if p:
        who = f"{who} ({p})" if n else f"{who} ({p})"
    if r_short:
        return f"{who}: {r_short}"
    return who


def generate_lead_summary(*, name: str, phone: str, request: str) -> str:
    """
    Best-effort AI summary.
    - If AI_PROVIDER=openai and OPENAI_API_KEY is set, uses OpenAI.
    - Otherwise falls back to a deterministic rules summary.
    """
    provider = (settings.ai_provider or "rules").lower()
    if provider != "openai" or not settings.openai_api_key.strip():
        return _rules_summary(name, phone, request)

    sys = (
        "You are a CRM assistant. Create a short lead summary (max 1 sentence, <= 25 words). "
        "Include what they want and any useful specifics. Do NOT add extra questions. "
        "Return plain text only."
    )
    user = f"Name: {name or ''}\nPhone: {phone or ''}\nRequest: {request or ''}\n"
    payload = {
        "model": settings.openai_model.strip() or "gpt-4.1-mini",
        "messages": [{"role": "system", "content": sys}, {"role": "user", "content": user}],
        "temperature": 0.2,
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
        return content or _rules_summary(name, phone, request)
    except Exception:
        return _rules_summary(name, phone, request)

