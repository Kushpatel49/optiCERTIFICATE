"""
Settings helpers for database connectivity.

This module centralizes the logic for resolving the database connection URL
so the application can seamlessly switch between the local SQLite fallback
and the production Supabase Postgres deployment.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional


def _load_streamlit_secrets() -> Optional[Dict[str, Any]]:
    """Attempt to read Streamlit secrets if running inside Streamlit."""
    try:
        import streamlit as st  # type: ignore
    except Exception:
        return None

    secrets_obj = getattr(st, "secrets", None)
    if secrets_obj is None:
        return None

    load_if_available = getattr(secrets_obj, "load_if_toml_exists", None)
    try:
        if callable(load_if_available) and not load_if_available():
            return None
        return dict(secrets_obj)
    except FileNotFoundError:
        return None
    except Exception:
        return None


def _find_project_root() -> Path:
    """Return the project root for placing the local SQLite database."""
    env_override = os.getenv("NETWORTH_APP_ROOT")
    if env_override:
        return Path(env_override).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def get_database_url() -> str:
    """
    Resolve the database URL in the following order:

    1. `DATABASE_URL` environment variable.
    2. Streamlit secrets under `database.url` or `supabase.url`.
    3. Fallback to a project-scoped SQLite database file.
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    secrets = _load_streamlit_secrets()
    if secrets:
        database_section = secrets.get("database")
        if isinstance(database_section, dict) and "url" in database_section:
            return str(database_section["url"])

        supabase_section = secrets.get("supabase")
        if isinstance(supabase_section, dict) and "db_url" in supabase_section:
            return str(supabase_section["db_url"])

        # Allow direct DATABASE_URL key in secrets
        direct_secret = secrets.get("DATABASE_URL")
        if isinstance(direct_secret, str):
            return direct_secret

    project_root = _find_project_root()
    sqlite_path = project_root / "networth.db"
    return f"sqlite:///{sqlite_path}"


def get_engine_kwargs(database_url: str) -> Dict[str, Any]:
    """
    Return engine keyword arguments for SQLAlchemy based on the driver.

    SQLite requires the `check_same_thread=False` flag for multi-threaded use,
    which Streamlit relies on.
    """
    if database_url.startswith("sqlite://"):
        return {"connect_args": {"check_same_thread": False}}
    return {}

