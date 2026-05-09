from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.notifications import get_notification, list_notifications, update_notification
from app.db.session import get_db
from app.schemas.notification import NotificationOut, NotificationUpdate

router = APIRouter()


@router.get("", response_model=list[NotificationOut])
def list_(
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    topic: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[NotificationOut]:
    return list_notifications(db, limit=limit, offset=offset, unread_only=unread_only, topic=topic)


@router.patch("/{notification_id}", response_model=NotificationOut)
def patch_(
    notification_id: int,
    payload: NotificationUpdate,
    db: Session = Depends(get_db),
) -> NotificationOut:
    n = get_notification(db, notification_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    return update_notification(db, n, read=payload.read)

