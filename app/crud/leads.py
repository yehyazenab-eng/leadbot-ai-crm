from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lead import Lead, LeadInteraction, LeadNote


def create_lead(
    db: Session,
    *,
    name: str,
    phone: str,
    email: str,
    request: str,
    source: str,
    summary: str = "",
    score: str = "Low",
) -> Lead:
    lead = Lead(
        name=name or "",
        phone=phone or "",
        email=email or "",
        request=request or "",
        summary=summary or "",
        score=score or "Low",
        source=source or "chat",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def list_leads(db: Session, *, limit: int = 50, offset: int = 0, stage: Optional[str] = None) -> list[Lead]:
    stmt = select(Lead).order_by(Lead.created_at.desc()).limit(limit).offset(offset)
    if stage:
        stmt = stmt.where(Lead.stage == stage)
    return list(db.execute(stmt).scalars().all())


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    return db.get(Lead, lead_id)


def update_lead(
    db: Session,
    lead: Lead,
    *,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    request: Optional[str] = None,
    summary: Optional[str] = None,
    score: Optional[str] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
) -> Lead:
    if name is not None:
        lead.name = name
    if phone is not None:
        lead.phone = phone
    if email is not None:
        lead.email = email
    if request is not None:
        lead.request = request
    if summary is not None:
        lead.summary = summary
    if score is not None:
        lead.score = score
    if stage is not None:
        lead.stage = stage
    if status is not None:
        lead.status = status
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def add_note(db: Session, *, lead_id: int, content: str, author: str) -> LeadNote:
    note = LeadNote(lead_id=lead_id, content=content, author=author or "system")
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def add_interaction(
    db: Session, *, lead_id: int, channel: str, direction: str, message: str
) -> LeadInteraction:
    interaction = LeadInteraction(
        lead_id=lead_id,
        channel=channel or "chat",
        direction=direction or "in",
        message=message or "",
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction

