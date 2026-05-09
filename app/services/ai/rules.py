from __future__ import annotations

from app.core.config import settings
from app.services.ai.base import AIProvider, AIResult


class RulesAI(AIProvider):
    def respond(self, message: str) -> AIResult:
        m = (message or "").strip().lower()

        if any(k in m for k in ["מחיר", "price", "cost", "כמה עולה"]):
            return AIResult(
                reply=f"המחיר מתחיל מ-{settings.base_price_ils}₪. רוצה להשאיר פרטים ונחזור אליך?",
                confidence=0.75,
            )

        if any(k in m for k in ["שעות", "פתוח", "hours", "open"]):
            return AIResult(reply=f"אנחנו פתוחים {settings.business_hours}.", confidence=0.7)

        if any(k in m for k in ["מיקום", "כתובת", "location", "address", "איפה אתם"]):
            return AIResult(reply=f"{settings.business_location}", confidence=0.7)

        return AIResult(
            reply="רוצה להשאיר פרטים? כתוב/י: שם, טלפון, ומה צריך — ונחזור אליך.",
            confidence=0.4,
        )

