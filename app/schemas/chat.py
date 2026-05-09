from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    channel: str = "chat"
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    lead_id: Optional[int] = None
    created_lead: bool = False

