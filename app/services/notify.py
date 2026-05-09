from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Optional

import httpx

from app.core.config import settings
from app.crud.notifications import create_notification
from app.db.session import SessionLocal


def notify_console(title: str, body: str) -> None:
    print(f"[notify] {title}\n{body}\n")


def notify_macos(title: str, body: str) -> None:
    if os.name != "posix":
        return
    if not shutil_which("osascript"):
        return
    safe_title = title.replace('"', "'")
    safe_body = body.replace('"', "'")
    os.system(f'osascript -e \'display notification "{safe_body}" with title "{safe_title}"\'')


def notify_webhook(payload: dict) -> None:
    url = settings.notify_webhook_url.strip()
    if not url:
        return
    with httpx.Client(timeout=10.0) as client:
        client.post(url, json=payload)


def notify_email(subject: str, body: str) -> None:
    if not (settings.smtp_host and settings.smtp_from and settings.smtp_to):
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = settings.smtp_to
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as s:
        s.starttls()
        if settings.smtp_username:
            s.login(settings.smtp_username, settings.smtp_password)
        s.send_message(msg)


def notify_lead_event(event: str, lead_id: int, name: str, phone: str, request: str) -> None:
    title = f"Lead {event}: #{lead_id}"
    body = f"Name: {name}\nPhone: {phone}\nRequest: {request}"
    try:
        db = SessionLocal()
        try:
            create_notification(db, topic="lead", event=event, title=title, body=body)
        finally:
            db.close()
    except Exception:
        # notifications are best-effort; don't block lead creation
        pass
    notify_console(title, body)  
    notify_webhook({"event": event, "lead_id": lead_id, "name": name, "phone": phone, "request": request})
    send_whatsapp_notification(phone, body)
    notify_email(subject=title, body=body)


def shutil_which(cmd: str) -> Optional[str]:
    paths = os.environ.get("PATH", "").split(os.pathsep)
    for p in paths:
        candidate = os.path.join(p, cmd)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None

def send_whatsapp_notification(phone, message):
    print(f"📲 Sending WhatsApp to {phone}: {message}")


