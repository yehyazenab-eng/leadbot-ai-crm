from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.leads import add_interaction, add_note, create_lead, get_lead, list_leads, update_lead
from app.db.session import get_db
from app.schemas.lead import (
    LeadCreate,
    LeadInteractionCreate,
    LeadInteractionOut,
    LeadNoteCreate,
    LeadNoteOut,
    LeadOut,
    LeadUpdate,
)
from app.services.ai.summarizer import generate_lead_summary
from app.services.ai.scoring import score_lead
from app.services.notify import notify_lead_event

router = APIRouter()


@router.post("", response_model=LeadOut)
def create(payload: LeadCreate, db: Session = Depends(get_db)) -> LeadOut:
    summary = generate_lead_summary(name=payload.name, phone=payload.phone, request=payload.request)
    score = score_lead(request=payload.request)
    lead = create_lead(
        db,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        request=payload.request,
        summary=summary,
        score=score,
        source=payload.source,
    )
    notify_lead_event("created", lead.id, lead.name, lead.phone, lead.request)
    return lead


@router.get("", response_model=list[LeadOut])
def list_(
    limit: int = 50, offset: int = 0, stage: Optional[str] = None, db: Session = Depends(get_db)
) -> list[LeadOut]:
    return list_leads(db, limit=limit, offset=offset, stage=stage)


@router.get("/{lead_id}", response_model=LeadOut)
def get_(lead_id: int, db: Session = Depends(get_db)) -> LeadOut:
    lead = get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadOut)
def patch_(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)) -> LeadOut:
    lead = get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    new_request = payload.request
    summary = generate_lead_summary(
        name=(payload.name if payload.name is not None else lead.name),
        phone=(payload.phone if payload.phone is not None else lead.phone),
        request=(new_request if new_request is not None else lead.request),
    )
    score = score_lead(request=(new_request if new_request is not None else lead.request))
    lead = update_lead(
        db,
        lead,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        request=new_request,
        summary=summary if new_request is not None else None,
        score=score if new_request is not None else None,
        stage=payload.stage,
        status=payload.status,
    )
    notify_lead_event("updated", lead.id, lead.name, lead.phone, lead.request)
    return lead


@router.post("/{lead_id}/notes", response_model=LeadNoteOut)
def add_note_(lead_id: int, payload: LeadNoteCreate, db: Session = Depends(get_db)) -> LeadNoteOut:
    lead = get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return add_note(db, lead_id=lead_id, content=payload.content, author=payload.author)


@router.post("/{lead_id}/interactions", response_model=LeadInteractionOut)
def add_interaction_(
    lead_id: int, payload: LeadInteractionCreate, db: Session = Depends(get_db)
) -> LeadInteractionOut:
    lead = get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return add_interaction(
        db, lead_id=lead_id, channel=payload.channel, direction=payload.direction, message=payload.message
    )

