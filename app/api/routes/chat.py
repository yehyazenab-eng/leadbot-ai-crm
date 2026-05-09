from __future__ import annotations

import re

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.leads import add_interaction, create_lead
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai.factory import get_ai_provider
from app.services.ai.scoring import score_lead
from app.services.ai.summarizer import generate_lead_summary
from app.services.notify import notify_lead_event

router = APIRouter()


PHONE_RE = re.compile(r"(\+?\d[\d \-]{7,}\d)")
EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")


def _extract_contact(message: str) -> tuple[str, str]:
    phone = ""
    email = ""
    if not message:
        return phone, email
    m1 = PHONE_RE.search(message)
    if m1:
        phone = m1.group(1).strip()
    m2 = EMAIL_RE.search(message)
    if m2:
        email = m2.group(1).strip()
    return phone, email


@router.post("/respond", response_model=ChatResponse)
def respond(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    provider = get_ai_provider()
    ai = provider.respond(payload.message)
    reply = ai.reply

    name = (payload.name or "").strip()
    phone = (payload.phone or "").strip()
    email = (payload.email or "").strip()

    if not phone or not email:
        p2, e2 = _extract_contact(payload.message)
        phone = phone or p2
        email = email or e2

    # Create a lead when we have *some* contact + a request intent.
    should_create = bool(phone or email) and len((payload.message or "").strip()) > 6
    if should_create:
        req = (payload.message or "").strip()
        summary = generate_lead_summary(name=name, phone=phone, request=req)
        score = score_lead(request=req)
        lead = create_lead(
            db,
            name=name,
            phone=phone,
            email=email,
            request=req,
            summary=summary,
            score=score,
            source=payload.channel,
        )
        add_interaction(db, lead_id=lead.id, channel=payload.channel, direction="in", message=payload.message)
        notify_lead_event("created", lead.id, lead.name, lead.phone, lead.request)
        return ChatResponse(reply=reply, lead_id=lead.id, created_lead=True)

    return ChatResponse(reply=reply, lead_id=None, created_lead=False)

