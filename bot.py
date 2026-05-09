import os

import httpx


API_BASE_URL = os.environ.get("LEADBOT_API", "http://127.0.0.1:8000")


def _fallback_rules(message: str) -> str:
    m = (message or "").strip().lower()
    if "מחיר" in m:
        return "המחיר מתחיל מ-150₪. רוצה להשאיר פרטים ונחזור אליך?"
    if "שעות" in m:
        return "אנחנו פתוחים 8:00–20:00."
    if "מיקום" in m:
        return "הכתובת: שדרות ירושלים 15 יפו."
    return "רוצה להשאיר פרטים? כתוב/י: שם, טלפון, ומה צריך — ונחזור אליך."


def respond(message: str) -> str:
    try:
        r = httpx.post(f"{API_BASE_URL}/chat/respond", json={"message": message}, timeout=5.0)
        r.raise_for_status()
        data = r.json()
        lead_id = data.get("lead_id")
        if lead_id:
            return f"{data.get('reply','')}\n(נשמר ליד #{lead_id})"
        return data.get("reply") or ""
    except Exception:
        return _fallback_rules(message)


if __name__ == "__main__":
    print(f"Lead bot CLI -> {API_BASE_URL}")
    while True:
        user_input = input("לקוח: ")
        print("בוט:", respond(user_input))
