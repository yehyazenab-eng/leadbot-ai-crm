from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.crud.leads import create_lead
from app.db.session import get_db
from app.services.ai.scoring import score_lead
from app.services.ai.summarizer import generate_lead_summary
from app.services.notify import notify_lead_event

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/lead", response_class=HTMLResponse)
def lead_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("public/lead.html", {"request": request})


@router.post("/lead")
def submit_lead(
    name: str = Form(""),
    phone: str = Form(...),
    request: str = Form(...),
    db: Session = Depends(get_db),
):
    summary = generate_lead_summary(name=name, phone=phone, request=request)
    score = score_lead(request=request)
    lead = create_lead(db, name=name, phone=phone, email="", request=request, summary=summary, score=score, source="web")
    notify_lead_event("created", lead.id, lead.name, lead.phone, lead.request)
    return RedirectResponse(url=f"/lead/thanks?lead_id={lead.id}", status_code=303)


@router.get("/lead/thanks", response_class=HTMLResponse)
def lead_thanks(request: Request, lead_id: Optional[int] = None) -> HTMLResponse:
    return templates.TemplateResponse("public/thanks.html", {"request": request, "lead_id": lead_id})

