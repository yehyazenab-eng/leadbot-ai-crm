from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    created_at: datetime
    topic: str
    event: str
    title: str
    body: str
    read: bool

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    read: Optional[bool] = None

