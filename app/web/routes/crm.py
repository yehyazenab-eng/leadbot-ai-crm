from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.crud.leads import get_lead, list_leads, update_lead
from app.crud.notifications import list_notifications, update_notification, get_notification
from app.db.session import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def crm_home(request: Request) -> HTMLResponse:
    return RedirectResponse(url="/crm/leads", status_code=302)


@router.get("/leads", response_class=HTMLResponse)
def crm_leads(
    request: Request,
    stage: Optional[str] = None,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    leads = list_leads(db, limit=200, offset=0, stage=stage)
    notifications = list_notifications(db, limit=20, offset=0, unread_only=True, topic="lead")
    return templates.TemplateResponse(
        "crm/leads.html",
        {
            "request": request,
            "leads": leads,
            "stage": stage,
            "notifications": notifications,
            "active": "leads",
        },
    )


@router.post("/leads/{lead_id}/stage")
def crm_set_stage(
    lead_id: int,
    stage: str = Form(...),
    db: Session = Depends(get_db),
):
    lead = get_lead(db, lead_id)
    if lead:
        update_lead(db, lead, stage=stage)
    return RedirectResponse(url="/crm/leads", status_code=303)


@router.get("/notifications", response_class=HTMLResponse)
def crm_notifications(
    request: Request,
    unread_only: bool = False,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    notifications = list_notifications(db, limit=200, offset=0, unread_only=unread_only, topic=None)
    return templates.TemplateResponse(
        "crm/notifications.html",
        {"request": request, "notifications": notifications, "unread_only": unread_only, "active": "notifications"},
    )


@router.post("/notifications/{notification_id}/read")
def crm_mark_notification_read(
    notification_id: int,
    read: str = Form("true"),
    next: str = Form("/crm/notifications"),
    db: Session = Depends(get_db),
):
    n = get_notification(db, notification_id)
    if n:
        update_notification(db, n, read=(read.lower() == "true"))
    return RedirectResponse(url=next, status_code=303)

