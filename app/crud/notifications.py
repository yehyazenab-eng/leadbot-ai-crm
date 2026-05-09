from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    *,
    topic: str,
    event: str,
    title: str,
    body: str,
) -> Notification:
    n = Notification(topic=topic or "lead", event=event or "", title=title or "", body=body or "", read=False)
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def list_notifications(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    topic: Optional[str] = None,
) -> list[Notification]:
    stmt = select(Notification).order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    if unread_only:
        stmt = stmt.where(Notification.read.is_(False))
    if topic:
        stmt = stmt.where(Notification.topic == topic)
    return list(db.execute(stmt).scalars().all())


def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    return db.get(Notification, notification_id)


def update_notification(db: Session, notification: Notification, *, read: Optional[bool] = None) -> Notification:
    if read is not None:
        notification.read = bool(read)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

