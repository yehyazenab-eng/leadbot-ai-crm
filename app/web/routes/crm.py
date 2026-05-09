from __future__ import annotations

import os
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

CRM_COOKIE_NAME = "crm_logged_in"


def get_crm_password() -> str:
    return os.getenv("CRM_PASSWORD", "change-me")


def is_logged_in(request: Request) -> bool:
    return request.cookies.get(CRM_COOKIE_NAME) == "yes"


def require_login(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(url="/crm/login", status_code=303)
    return None


@router.get("", response_class=HTMLResponse)
def crm_home(request: Request) -> HTMLResponse:
    return RedirectResponse(url="/crm/leads", status_code=302)


@router.get("/login", response_class=HTMLResponse)
def crm_login_page(request: Request) -> HTMLResponse:
    html = """
    <!doctype html>
    <html>
    <head>
        <title>CRM Login</title>
        <style>
            body {
                margin: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: radial-gradient(circle at top left, #2b1558, #080b12 55%);
                color: white;
                font-family: Arial, sans-serif;
            }
            .card {
                width: 360px;
                padding: 28px;
                border: 1px solid rgba(255,255,255,.14);
                border-radius: 18px;
                background: rgba(20, 22, 32, .92);
                box-shadow: 0 20px 60px rgba(0,0,0,.35);
            }
            h1 { margin: 0 0 8px; font-size: 24px; }
            p { color: #b8b8c8; margin-bottom: 22px; }
            input {
                width: 100%;
                box-sizing: border-box;
                padding: 12px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,.18);
                background: #0d111a;
                color: white;
                margin-bottom: 14px;
            }
            button {
                width: 100%;
                padding: 12px;
                border: 0;
                border-radius: 10px;
                background: #6d3bd6;
                color: white;
                font-weight: bold;
                cursor: pointer;
            }
            .hint {
                margin-top: 14px;
                font-size: 12px;
                color: #888;
            }
        </style>
    </head>
    <body>
        <form class="card" method="post" action="/crm/login">
            <h1>CRM Login</h1>
            <p>Enter your CRM password.</p>
            <input type="password" name="password" placeholder="Password" required autofocus>
            <button type="submit">Login</button>
            <div class="hint">Protected CRM access</div>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(html)


@router.post("/login")
def crm_login(password: str = Form(...)):
    if password != get_crm_password():
        return HTMLResponse(
            """
            <h2 style="font-family:Arial;color:white;background:#0b0f18;padding:40px;">
                Wrong password.
                <br><br>
                <a style="color:#8b5cf6;" href="/crm/login">Try again</a>
            </h2>
            """,
            status_code=401,
        )

    response = RedirectResponse(url="/crm/leads", status_code=303)
    response.set_cookie(
        key=CRM_COOKIE_NAME,
        value="yes",
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.get("/logout")
def crm_logout():
    response = RedirectResponse(url="/crm/login", status_code=303)
    response.delete_cookie(CRM_COOKIE_NAME)
    return response


@router.get("/leads", response_class=HTMLResponse)
def crm_leads(
    request: Request,
    stage: Optional[str] = None,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    guard = require_login(request)
    if guard:
        return guard

    leads = list_leads(db, limit=200, offset=0, stage=stage)
    notifications = list_notifications(db, limit=20, offset=0, unread_only=True)

    return templates.TemplateResponse(
        name="crm/leads.html",
        request=request,
        context={
            "request": request,
            "leads": leads,
            "stage": stage,
            "notifications": notifications,
            "active": "leads",
        },
    )


@router.post("/leads/{lead_id}/stage")
def crm_set_stage(
    request: Request,
    lead_id: int,
    stage: str = Form(...),
    db: Session = Depends(get_db),
):
    guard = require_login(request)
    if guard:
        return guard

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
    guard = require_login(request)
    if guard:
        return guard

    notifications = list_notifications(db, limit=200, offset=0, unread_only=unread_only, topic=None)

    return templates.TemplateResponse(
        name="crm/notifications.html",
        request=request,
        context={
            "request": request,
            "notifications": notifications,
            "unread_only": unread_only,
            "active": "notifications",
        },
    )


@router.post("/notifications/{notification_id}/read")
def crm_mark_notification_read(
    request: Request,
    notification_id: int,
    read: str = Form("true"),
    next: str = Form("/crm/notifications"),
    db: Session = Depends(get_db),
):
    guard = require_login(request)
    if guard:
        return guard

    n = get_notification(db, notification_id)
    if n:
        update_notification(db, n, read=(read.lower() == "true"))
    return RedirectResponse(url=next, status_code=303)