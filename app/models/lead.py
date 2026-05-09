from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    name: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    phone: Mapped[str] = mapped_column(String(50), default="", nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(320), default="", nullable=False, index=True)
    request: Mapped[str] = mapped_column(Text, default="", nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    score: Mapped[str] = mapped_column(String(10), default="Low", nullable=False, index=True)  # High/Medium/Low

    source: Mapped[str] = mapped_column(String(100), default="chat", nullable=False)
    stage: Mapped[str] = mapped_column(String(50), default="new", nullable=False, index=True)  # new/contacted/won/lost
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False, index=True)  # open/closed

    notes: Mapped[list["LeadNote"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    interactions: Mapped[list["LeadInteraction"]] = relationship(back_populates="lead", cascade="all, delete-orphan")


class LeadNote(Base):
    __tablename__ = "lead_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(120), default="system", nullable=False)

    lead: Mapped["Lead"] = relationship(back_populates="notes")


class LeadInteraction(Base):
    __tablename__ = "lead_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    channel: Mapped[str] = mapped_column(String(50), default="chat", nullable=False)  # chat/phone/email/whatsapp
    direction: Mapped[str] = mapped_column(String(10), default="in", nullable=False)  # in/out
    message: Mapped[str] = mapped_column(Text, default="", nullable=False)

    lead: Mapped["Lead"] = relationship(back_populates="interactions")

