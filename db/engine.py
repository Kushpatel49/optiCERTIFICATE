"""
SQLAlchemy engine factory utilities.

Provides a cached engine instance that reflects the current configuration.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import create_engine  # type: ignore[import-not-found]
from sqlalchemy.engine import Engine  # type: ignore[import-not-found]

from .settings import get_database_url, get_engine_kwargs

_ENGINE: Engine | None = None


def get_engine(echo: bool = False) -> Engine:
    """
    Return a cached SQLAlchemy engine.

    Parameters
    ----------
    echo:
        When True, SQLAlchemy will echo SQL statements to stdout. Useful for
        debugging, but should remain False in production.
    """
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    database_url = get_database_url()
    kwargs: dict[str, Any] = get_engine_kwargs(database_url)
    _ENGINE = create_engine(database_url, echo=echo, **kwargs)
    return _ENGINE


@lru_cache(maxsize=1)
def get_database_url_cached() -> str:
    """Expose the resolved database URL for tooling (e.g., Alembic)."""
    return get_database_url()


def init_db() -> None:
    """
    Create all tables using the current metadata.

    This is primarily intended for quick-start local development on SQLite.
    Production deployments should rely on Alembic migrations instead.
    """
    from . import models

    engine = get_engine()
    models.Base.metadata.create_all(bind=engine)

