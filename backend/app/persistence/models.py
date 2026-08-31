"""SQLAlchemy ORM rows for sessions, messages, case records, and traces.

Timestamps are stored as ISO-8601 UTC strings so SQLite round-trips remain
timezone-exact. Structured payloads (StructuredCase, DecisionTrace) are kept
as JSON text columns; domain validation happens at the pydantic boundary.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.database import Base


class SessionRow(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    preferred_language: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    followup_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class MessageRow(Base):
    __tablename__ = "messages"

    seq: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(
        Text, ForeignKey("sessions.id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    lang: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)


class CaseRecordRow(Base):
    __tablename__ = "case_records"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    session_id: Mapped[str] = mapped_column(
        Text, ForeignKey("sessions.id"), nullable=False, index=True
    )
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    case_json: Mapped[str] = mapped_column(Text, nullable=False)


class TraceRecordRow(Base):
    __tablename__ = "trace_records"

    seq: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(
        Text, ForeignKey("sessions.id"), nullable=False, index=True
    )
    step: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    trace_json: Mapped[str] = mapped_column(Text, nullable=False)
