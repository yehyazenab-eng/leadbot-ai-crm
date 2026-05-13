from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Optional

import httpx

from app.core.config import settings
from app.crud.notifications import create_notification
from app.db.session import SessionLocal


CRM_URL = os.environ.get("CRM_URL", "https://leadbot-ai-crm.onrender.com/crm/leads")


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

    try:
        with httpx.Client(timeout=10.0) as client:
            client.post(url, json=payload)
    except Exception as error:
        print(f"[notify_webhook_failed] {error}")


def notify_email(subject: str, body: str) -> None:
    if not (settings.smtp_host and settings.smtp_from and settings.smtp_to):
        print("[notify_email] SMTP settings missing. Email was not sent.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = settings.smtp_to
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.starttls()

            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)

            smtp.send_message(msg)

        print(f"[notify_email] Email sent to {settings.smtp_to}")

    except Exception as error:
        print(f"[notify_email_failed] {error}")


def notify_lead_event(event: str, lead_id: int, name: str, phone: str, request: str) -> None:
    title = f"New lead {event}: #{lead_id}"

    body = (
        f"New lead received\n\n"
        f"Lead ID: #{lead_id}\n"
        f"Name: {name or 'Unknown'}\n"
        f"Phone: {phone or 'Missing'}\n"
        f"Request: {request or 'No request'}\n\n"
        f"Open CRM:\n"
        f"{CRM_URL}\n"
    )

    try:
        db = SessionLocal()
        try:
            create_notification(db, topic="lead", event=event, title=title, body=body)
        finally:
            db.close()
    except Exception as error:
        print(f"[create_notification_failed] {error}")

    notify_console(title, body)

    notify_webhook(
        {
            "event": event,
            "lead_id": lead_id,
            "name": name,
            "phone": phone,
            "request": request,
            "crm_url": CRM_URL,
        }
    )

    notify_email(subject=title, body=body)


def shutil_which(cmd: str) -> Optional[str]:
    paths = os.environ.get("PATH", "").split(os.pathsep)

    for path in paths:
        candidate = os.path.join(path, cmd)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return None
    