from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.leads import create_lead
from app.db.session import get_db
from app.models.lead import Lead
from app.services.ai.scoring import score_lead
from app.services.ai.summarizer import generate_lead_summary
from app.services.notify import notify_lead_event

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

DUPLICATE_WINDOW_MINUTES = 10


def normalize_text(value: str) -> str:
    return " ".join((value or "").strip().split())


def normalize_phone(value: str) -> str:
    return "".join(ch for ch in (value or "").strip() if ch.isdigit() or ch == "+")


def find_recent_duplicate_lead(
    db: Session,
    phone: str,
    request_text: str,
    source: str,
) -> Optional[Lead]:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=DUPLICATE_WINDOW_MINUTES)

    stmt = (
        select(Lead)
        .where(Lead.phone == phone)
        .where(Lead.request == request_text)
        .where(Lead.source == source)
        .where(Lead.created_at >= cutoff)
        .order_by(Lead.created_at.desc())
        .limit(1)
    )

    try:
        return db.execute(stmt).scalars().first()
    except OperationalError as error:
        print(f"[duplicate_check_failed_operational] {error}")
        db.rollback()
        return None
    except SQLAlchemyError as error:
        print(f"[duplicate_check_failed_sqlalchemy] {error}")
        db.rollback()
        return None
    except Exception as error:
        print(f"[duplicate_check_failed_unknown] {error}")
        db.rollback()
        return None


@router.get("/lead", response_class=HTMLResponse)
def lead_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        name="public/lead.html",
        request=request,
        context={"request": request},
    )


@router.post("/lead")
def submit_lead(
    name: str = Form(""),
    phone: str = Form(...),
    request: str = Form(...),
    source: str = Form("website"),
    db: Session = Depends(get_db),
):
    clean_name = normalize_text(name)
    clean_phone = normalize_phone(phone)
    clean_request = normalize_text(request)
    clean_source = normalize_text(source).lower() or "website"

    duplicate = find_recent_duplicate_lead(
        db=db,
        phone=clean_phone,
        request_text=clean_request,
        source=clean_source,
    )

    if duplicate:
        return RedirectResponse(url=f"/lead/thanks?lead_id={duplicate.id}", status_code=303)

    summary = generate_lead_summary(name=clean_name, phone=clean_phone, request=clean_request)
    score = score_lead(request=clean_request)

    try:
        lead = create_lead(
            db,
            name=clean_name,
            phone=clean_phone,
            email="",
            request=clean_request,
            summary=summary,
            score=score,
            source=clean_source,
        )
    except OperationalError as error:
        print(f"[create_lead_failed_operational] {error}")
        db.rollback()
        raise
    except SQLAlchemyError as error:
        print(f"[create_lead_failed_sqlalchemy] {error}")
        db.rollback()
        raise

    notify_lead_event("created", lead.id, lead.name, lead.phone, lead.request)
    return RedirectResponse(url=f"/lead/thanks?lead_id={lead.id}", status_code=303)


@router.get("/lead/thanks", response_class=HTMLResponse)
def lead_thanks(request: Request, lead_id: Optional[int] = None) -> HTMLResponse:
    return templates.TemplateResponse(
        name="public/thanks.html",
        request=request,
        context={"request": request, "lead_id": lead_id},
    )
    