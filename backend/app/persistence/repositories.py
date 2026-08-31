"""Repositories mapping domain models to persistence rows.

Each repository owns its unit of work (one SQLAlchemy session per operation),
so callers never manage transactions. Timestamps round-trip as ISO-8601 UTC.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import sessionmaker

from app.models import (
    DecisionTrace,
    Language,
    Message,
    MessageRole,
    Session,
    SessionStatus,
    StructuredCase,
)
from app.persistence.models import CaseRecordRow, MessageRow, SessionRow, TraceRecordRow


def _new_id() -> str:
    return uuid.uuid4().hex


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


class SessionRepository:
    def __init__(self, session_factory: sessionmaker[SASession]) -> None:
        self._session_factory = session_factory

    def create(self, session: Session) -> None:
        with self._session_factory() as sa:
            sa.add(
                SessionRow(
                    id=session.id,
                    created_at=session.created_at.isoformat(),
                    preferred_language=session.preferred_language.value,
                    status=session.status.value,
                    followup_rounds=0,
                )
            )
            sa.commit()

    def get(self, session_id: str) -> Session | None:
        with self._session_factory() as sa:
            row = sa.get(SessionRow, session_id)
            if row is None:
                return None
            return self._to_domain(row)

    def set_status(self, session_id: str, status: SessionStatus) -> None:
        with self._session_factory() as sa:
            row = sa.get(SessionRow, session_id)
            if row is not None:
                row.status = status.value
                sa.commit()

    def increment_followup_rounds(self, session_id: str) -> int:
        with self._session_factory() as sa:
            row = sa.get(SessionRow, session_id)
            if row is None:
                raise KeyError(session_id)
            row.followup_rounds += 1
            sa.commit()
            return row.followup_rounds

    def followup_rounds(self, session_id: str) -> int:
        with self._session_factory() as sa:
            row = sa.get(SessionRow, session_id)
            if row is None:
                raise KeyError(session_id)
            return row.followup_rounds

    @staticmethod
    def _to_domain(row: SessionRow) -> Session:
        return Session(
            id=row.id,
            created_at=_parse_iso(row.created_at),
            preferred_language=Language(row.preferred_language),
            status=SessionStatus(row.status),
        )


class MessageRepository:
    def __init__(self, session_factory: sessionmaker[SASession]) -> None:
        self._session_factory = session_factory

    def append(self, message: Message) -> None:
        with self._session_factory() as sa:
            sa.add(
                MessageRow(
                    id=message.id,
                    session_id=message.session_id,
                    role=message.role.value,
                    text=message.text,
                    lang=message.lang.value,
                    created_at=message.created_at.isoformat(),
                )
            )
            sa.commit()

    def list_for_session(self, session_id: str) -> list[Message]:
        with self._session_factory() as sa:
            rows = sa.scalars(
                select(MessageRow)
                .where(MessageRow.session_id == session_id)
                .order_by(MessageRow.seq)
            ).all()
            return [
                Message(
                    id=row.id,
                    session_id=row.session_id,
                    role=MessageRole(row.role),
                    text=row.text,
                    lang=Language(row.lang),
                    created_at=_parse_iso(row.created_at),
                )
                for row in rows
            ]


class CaseRepository:
    def __init__(self, session_factory: sessionmaker[SASession]) -> None:
        self._session_factory = session_factory

    def append(self, session_id: str, case: StructuredCase) -> None:
        with self._session_factory() as sa:
            sa.add(
                CaseRecordRow(
                    id=_new_id(),
                    session_id=session_id,
                    created_at=_now_iso(),
                    case_json=case.model_dump_json(),
                )
            )
            sa.commit()

    def latest(self, session_id: str) -> StructuredCase | None:
        with self._session_factory() as sa:
            row = sa.scalars(
                select(CaseRecordRow)
                .where(CaseRecordRow.session_id == session_id)
                .order_by(CaseRecordRow.created_at.desc())
            ).first()
            return StructuredCase.model_validate_json(row.case_json) if row else None


class TraceRepository:
    def __init__(self, session_factory: sessionmaker[SASession]) -> None:
        self._session_factory = session_factory

    def append(self, session_id: str, trace: DecisionTrace) -> None:
        with self._session_factory() as sa:
            sa.add(
                TraceRecordRow(
                    id=_new_id(),
                    session_id=session_id,
                    step=trace.step,
                    created_at=_now_iso(),
                    trace_json=trace.model_dump_json(),
                )
            )
            sa.commit()

    def list_for_session(self, session_id: str) -> list[DecisionTrace]:
        with self._session_factory() as sa:
            rows = sa.scalars(
                select(TraceRecordRow)
                .where(TraceRecordRow.session_id == session_id)
                .order_by(TraceRecordRow.seq)
            ).all()
            return [DecisionTrace.model_validate_json(row.trace_json) for row in rows]
