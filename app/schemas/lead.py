from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    request: str = ""
    source: str = "chat"


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    request: Optional[str] = None
    stage: Optional[str] = None
    status: Optional[str] = None


class LeadOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    phone: str
    email: str
    request: str
    summary: str
    score: str
    source: str
    stage: str
    status: str

    class Config:
        from_attributes = True


class LeadNoteCreate(BaseModel):
    content: str = Field(min_length=1)
    author: str = "system"


class LeadNoteOut(BaseModel):
    id: int
    lead_id: int
    created_at: datetime
    content: str
    author: str

    class Config:
        from_attributes = True


class LeadInteractionCreate(BaseModel):
    channel: str = "chat"
    direction: str = "in"
    message: str = ""


class LeadInteractionOut(BaseModel):
    id: int
    lead_id: int
    created_at: datetime
    channel: str
    direction: str
    message: str

    class Config:
        from_attributes = True

