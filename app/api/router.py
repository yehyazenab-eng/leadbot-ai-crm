from fastapi import APIRouter

from app.api.routes import chat, leads, notifications

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

