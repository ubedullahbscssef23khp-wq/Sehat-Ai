"""Database engine setup for SQLite persistence (ARCHITECTURE.md §2).

SQLite gives zero-infrastructure persistence for the demo; SQLAlchemy keeps
the models portable to PostgreSQL via a connection-string change only.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all persistence rows."""


def build_engine(db_path: Path) -> Engine:
    """Create an engine for the SQLite file, creating its parent directory.

    check_same_thread is disabled because async request handlers may touch the
    engine from the event-loop thread while tests use their own threads.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )


def init_db(engine: Engine) -> None:
    """Create all tables if they do not exist yet."""
    # Imported here so the models are registered on Base before create_all.
    from app.persistence import models  # noqa: F401

    Base.metadata.create_all(engine)
