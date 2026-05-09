from __future__ import annotations

import os

import httpx


def main() -> None:
    base = os.environ.get("LEADBOT_API", "http://127.0.0.1:8000").rstrip("/")
    with httpx.Client(timeout=10.0) as c:
        r = c.get(f"{base}/health")
        r.raise_for_status()
        print("health:", r.json())

        r = c.post(
            f"{base}/chat/respond",
            json={"message": "יוסי, 0501234567, רוצה להזמין", "channel": "chat"},
        )
        r.raise_for_status()
        print("chat:", r.json())

        r = c.get(f"{base}/leads", params={"limit": 5})
        r.raise_for_status()
        print("leads:", [x["id"] for x in r.json()])

        r = c.get(f"{base}/notifications", params={"limit": 5})
        r.raise_for_status()
        print("notifications:", [x["id"] for x in r.json()])


if __name__ == "__main__":
    main()

