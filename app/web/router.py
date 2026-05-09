from __future__ import annotations

from fastapi import APIRouter

from app.web.routes import crm, public

web_router = APIRouter()
web_router.include_router(crm.router, prefix="/crm", tags=["crm"])
web_router.include_router(public.router, tags=["public"])

