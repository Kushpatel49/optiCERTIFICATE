"""
Repository layer encapsulating persistence operations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import NetWorthData

from . import models as orm
from .serializers import certificate_to_networth_data, networth_to_certificate_model
from .session import get_session


class RepositoryError(RuntimeError):
    """Raised when a persistence operation fails."""


@dataclass(slots=True)
class CertificateSummary:
    id: str
    individual_name: str
    certificate_date: str
    net_worth_inr: float
    created_at: str


@dataclass(slots=True)
class PersonSummary:
    id: str
    display_name: str
    email: Optional[str]
    phone_number: Optional[str]


@dataclass(slots=True)
class CertificateDetail:
    id: str
    person_id: Optional[str]
    data: NetWorthData


def create_person(
    session: Session,
    *,
    display_name: str,
    email: Optional[str] = None,
    phone_number: Optional[str] = None,
    notes: Optional[str] = None,
) -> orm.Person:
    """Persist a person entity."""
    person = orm.Person(
        display_name=display_name,
        email=email,
        phone_number=phone_number,
        notes=notes,
    )
    session.add(person)
    session.flush()
    session.refresh(person)
    return person


def save_person(
    *,
    display_name: str,
    email: Optional[str] = None,
    phone_number: Optional[str] = None,
    notes: Optional[str] = None,
) -> orm.Person:
    """Create a person using a managed session."""
    try:
        with get_session() as session:
            return create_person(
                session,
                display_name=display_name,
                email=email,
                phone_number=phone_number,
                notes=notes,
            )
    except SQLAlchemyError as exc:
        raise RepositoryError("Failed to store person") from exc


def list_persons() -> list[PersonSummary]:
    """Return all persons ordered by display name."""
    with get_session() as session:
        stmt = (
            select(
                orm.Person.id,
                orm.Person.display_name,
                orm.Person.email,
                orm.Person.phone_number,
            )
            .order_by(orm.Person.display_name.asc())
        )
        rows = session.execute(stmt).all()
        return [
            PersonSummary(
                id=row.id,
                display_name=row.display_name,
                email=row.email,
                phone_number=row.phone_number,
            )
            for row in rows
        ]


def create_certificate(
    session: Session,
    data: NetWorthData,
    *,
    person_id: Optional[str] = None,
    document_bytes: Optional[bytes] = None,
    document_file_name: Optional[str] = None,
    document_mime_type: Optional[str] = None,
    extra_metadata: Optional[dict] = None,
) -> orm.Certificate:
    """Persist a certificate and return the ORM entity."""
    certificate = networth_to_certificate_model(
        data,
        person_id=person_id,
        document_bytes=document_bytes,
        document_file_name=document_file_name,
        document_mime_type=document_mime_type,
        extra_metadata=extra_metadata,
    )
    session.add(certificate)
    session.flush()
    session.refresh(certificate)
    return certificate


def save_certificate(
    data: NetWorthData,
    *,
    person_id: Optional[str] = None,
    document_bytes: Optional[bytes] = None,
    document_file_name: Optional[str] = None,
    document_mime_type: Optional[str] = None,
    extra_metadata: Optional[dict] = None,
) -> orm.Certificate:
    """
    Convenience wrapper to persist a certificate using a managed session.
    """
    try:
        with get_session() as session:
            certificate = create_certificate(
                session,
                data,
                person_id=person_id,
                document_bytes=document_bytes,
                document_file_name=document_file_name,
                document_mime_type=document_mime_type,
                extra_metadata=extra_metadata,
            )
            return certificate
    except SQLAlchemyError as exc:
        raise RepositoryError("Failed to store certificate") from exc


def get_certificate(session: Session, certificate_id: str) -> Optional[orm.Certificate]:
    """Fetch a certificate ORM entity by ID."""
    stmt = select(orm.Certificate).where(orm.Certificate.id == certificate_id)
    return session.scalar(stmt)


def get_certificate_with_data(certificate_id: str) -> Optional[NetWorthData]:
    """Retrieve and deserialize a certificate by ID using a managed session."""
    with get_session() as session:
        certificate = get_certificate(session, certificate_id)
        if certificate is None:
            return None
        return certificate_to_networth_data(certificate)


def get_certificate_detail(certificate_id: str) -> Optional[CertificateDetail]:
    """Fetch certificate data along with associated person information."""
    with get_session() as session:
        certificate = get_certificate(session, certificate_id)
        if certificate is None:
            return None
        data = certificate_to_networth_data(certificate)
        return CertificateDetail(
            id=certificate.id,
            person_id=certificate.person_id,
            data=data,
        )


def list_recent_certificates(
    *,
    limit: int = 10,
    person_id: Optional[str] = None,
) -> list[CertificateSummary]:
    """Return lightweight summaries of the most recent certificates."""
    with get_session() as session:
        stmt = (
            select(
                orm.Certificate.id,
                orm.Certificate.individual_name,
                orm.Certificate.certificate_date,
                orm.Certificate.net_worth_inr,
                orm.Certificate.created_at,
            )
            .order_by(orm.Certificate.created_at.desc())
            .limit(limit)
        )
        if person_id:
            stmt = stmt.where(orm.Certificate.person_id == person_id)
        rows = session.execute(stmt).all()
        return [
            CertificateSummary(
                id=row.id,
                individual_name=row.individual_name,
                certificate_date=row.certificate_date,
                net_worth_inr=row.net_worth_inr,
                created_at=row.created_at.isoformat() if row.created_at else "",
            )
            for row in rows
        ]


def list_certificates_for_person(
    person_id: str,
    *,
    limit: int = 20,
) -> list[CertificateSummary]:
    """Return certificate summaries for a specific person."""
    return list_recent_certificates(limit=limit, person_id=person_id)


def load_certificate_snapshot(certificate_id: str) -> Optional[dict]:
    """
    Fetch only the JSON snapshot for a certificate (no relationships).
    Useful for lightweight API-like scenarios.
    """
    with get_session() as session:
        stmt = select(orm.Certificate.data_snapshot).where(
            orm.Certificate.id == certificate_id
        )
        snapshot = session.scalar(stmt)
        if snapshot is None:
            return None
        return json.loads(snapshot)


def list_certificates(
    session: Session,
    *,
    offset: int = 0,
    limit: int = 20,
) -> Iterable[orm.Certificate]:
    """Iterable of certificates ordered by creation date."""
    stmt = (
        select(orm.Certificate)
        .order_by(orm.Certificate.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return session.scalars(stmt)

