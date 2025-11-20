"""
Session helpers for database interactions.

Exposes a context-managed session factory tailored for Streamlit usage.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session, sessionmaker

from .engine import get_engine

SessionLocal = sessionmaker(
    bind=get_engine(),
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@contextmanager
def get_session() -> Iterator[Session]:
    """
    Provide a transactional scope around a series of operations.

    Usage:
        with get_session() as session:
            session.add(...)
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

