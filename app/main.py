from __future__ import annotations

from fastapi import FastAPI

from app.api.router import api_router
from app.db.base import init_db
from app.web.router import web_router

app = FastAPI(title="AI Lead Bot", version="0.1.0")
app.include_router(api_router)
app.include_router(web_router)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"ok": True}

