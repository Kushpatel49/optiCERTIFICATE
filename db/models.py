"""
SQLAlchemy ORM models mirroring the NetWorthData structure.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


def generate_uuid() -> str:
    """Produce a random UUID string."""
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    """Base declarative class."""


class Person(Base):
    """Represents an individual for whom certificates are generated."""

    __tablename__ = "persons"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    certificates: Mapped[List["Certificate"]] = relationship(
        back_populates="person"
    )


class Certificate(Base):
    """Root certificate metadata and snapshot."""

    __tablename__ = "certificates"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    person_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("persons.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Display name for quick listing (typically derived from the individuals list)
    individual_name: Mapped[str] = mapped_column(String(255), nullable=False)
    certificate_date: Mapped[str] = mapped_column(String(32), nullable=False)
    engagement_date: Mapped[str] = mapped_column(String(32), nullable=False)
    embassy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    embassy_address: Mapped[str] = mapped_column(Text, nullable=False)

    # Currency settings
    foreign_currency: Mapped[str] = mapped_column(String(8), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Float, nullable=False)

    # Section notes
    bank_accounts_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    insurance_policies_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pf_accounts_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deposits_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nps_accounts_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mutual_funds_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shares_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vehicles_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    post_office_schemes_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    partnership_firms_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gold_holdings_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    properties_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    liabilities_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # CA details
    ca_firm_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ca_frn: Mapped[str] = mapped_column(String(32), nullable=False)
    ca_partner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ca_membership_no: Mapped[str] = mapped_column(String(64), nullable=False)
    ca_designation: Mapped[str] = mapped_column(String(128), nullable=False)
    ca_place: Mapped[str] = mapped_column(String(128), nullable=False)

    # Precomputed totals
    total_movable_assets_inr: Mapped[float] = mapped_column(Float, nullable=False)
    total_immovable_assets_inr: Mapped[float] = mapped_column(Float, nullable=False)
    total_liabilities_inr: Mapped[float] = mapped_column(Float, nullable=False)
    net_worth_inr: Mapped[float] = mapped_column(Float, nullable=False)
    net_worth_foreign: Mapped[float] = mapped_column(Float, nullable=False)

    # Snapshots & documents
    data_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_file_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    document_mime_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    document_file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    document_bytes: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)

    person: Mapped[Optional[Person]] = relationship(back_populates="certificates")

    # Individuals covered by this certificate
    individuals: Mapped[List["CertificateIndividualModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )

    # Relationships
    bank_accounts: Mapped[List["BankAccountModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    insurance_policies: Mapped[List["InsurancePolicyModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    pf_accounts: Mapped[List["PFAccountModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    deposits: Mapped[List["DepositModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    nps_accounts: Mapped[List["NPSAccountModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    mutual_funds: Mapped[List["MutualFundModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    shares: Mapped[List["ShareModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    vehicles: Mapped[List["VehicleModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    post_office_schemes: Mapped[List["PostOfficeSchemeModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    partnership_firms: Mapped[List["PartnershipFirmModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    gold_holdings: Mapped[List["GoldHoldingModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    properties: Mapped[List["PropertyModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )
    liabilities: Mapped[List["LiabilityModel"]] = relationship(
        back_populates="certificate", cascade="all, delete-orphan"
    )

    def snapshot_dict(self) -> dict[str, Any]:
        """Return the JSON snapshot as a Python dict."""
        return json.loads(self.data_snapshot)


class BankAccountModel(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_number: Mapped[str] = mapped_column(String(128), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(255), nullable=False)
    balance_inr: Mapped[float] = mapped_column(Float, nullable=False)
    statement_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    certificate: Mapped[Certificate] = relationship(back_populates="bank_accounts")


class InsurancePolicyModel(Base):
    __tablename__ = "insurance_policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    policy_number: Mapped[str] = mapped_column(String(128), nullable=False)
    amount_inr: Mapped[float] = mapped_column(Float, nullable=False)

    certificate: Mapped[Certificate] = relationship(back_populates="insurance_policies")


class PFAccountModel(Base):
    __tablename__ = "pf_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    pf_account_number: Mapped[str] = mapped_column(String(128), nullable=False)
    amount_inr: Mapped[float] = mapped_column(Float, nullable=False)

    certificate: Mapped[Certificate] = relationship(back_populates="pf_accounts")


class DepositModel(Base):
    __tablename__ = "deposits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_number: Mapped[str] = mapped_column(String(128), nullable=False)
    amount_inr: Mapped[float] = mapped_column(Float, nullable=False)

    certificate: Mapped[Certificate] = relationship(back_populates="deposits")


class NPSAccountModel(Base):
    __tablename__ = "nps_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    pran_number: Mapped[str] = mapped_column(String(128), nullable=False)
    amount_inr: Mapped[float] = mapped_column(Float, nullable=False)

    certificate: Mapped[Certificate] = relationship(back_populates="nps_accounts")


class MutualFundModel(Base):
    __tablename__ = "mutual_funds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    folio_number: Mapped[str] = mapped_column(String(128), nullable=False)
    policy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_inr: Mapped[float] = mapped_column(Float, nullable=False)

    certificate: Mapped[Certificate] = relationship(back_populates="mutual_funds")


class ShareModel(Base):
    __tablename__ = "shares"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    num_shares: Mapped[int] = mapped_column(Integer, nullable=False)
    market_price_inr: Mapped[float] = mapped_column(Float, nullable=False)

    certificate: Mapped[Certificate] = relationship(back_populates="shares")


class VehicleModel(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    vehicle_type: Mapped[str] = mapped_column(String(64), nullable=False)
    make_model_year: Mapped[str] = mapped_column(String(255), nullable=False)
    registration_number: Mapped[str] = mapped_column(String(64), nullable=False)
    market_value_inr: Mapped[float] = mapped_column(Float, nullable=False)

    certificate: Mapped[Certificate] = relationship(back_populates="vehicles")


class PostOfficeSchemeModel(Base):
    __tablename__ = "post_office_schemes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    scheme_type: Mapped[str] = mapped_column(String(255), nullable=False)
    account_number: Mapped[str] = mapped_column(String(128), nullable=False)
    amount_inr: Mapped[float] = mapped_column(Float, nullable=False)

    certificate: Mapped[Certificate] = relationship(back_populates="post_office_schemes")


class PartnershipFirmModel(Base):
    __tablename__ = "partnership_firms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    firm_name: Mapped[str] = mapped_column(String(255), nullable=False)
    partner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    holding_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    capital_balance_inr: Mapped[float] = mapped_column(Float, nullable=False)
    valuation_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    certificate: Mapped[Certificate] = relationship(back_populates="partnership_firms")


class GoldHoldingModel(Base):
    __tablename__ = "gold_holdings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    weight_grams: Mapped[float] = mapped_column(Float, nullable=False)
    rate_per_10g: Mapped[float] = mapped_column(Float, nullable=False)
    valuation_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    valuer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    certificate: Mapped[Certificate] = relationship(back_populates="gold_holdings")


class PropertyModel(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    property_type: Mapped[str] = mapped_column(String(128), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    valuation_inr: Mapped[float] = mapped_column(Float, nullable=False)
    valuation_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    valuer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    certificate: Mapped[Certificate] = relationship(back_populates="properties")


class LiabilityModel(Base):
    __tablename__ = "liabilities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    certificate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_inr: Mapped[float] = mapped_column(Float, nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    certificate: Mapped[Certificate] = relationship(back_populates="liabilities")


class CertificateIndividualModel(Base):
    """
    Represents an individual (name, passport, address) covered by a certificate.
    """

    __tablename__ = "certificate_individuals"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    certificate_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("certificates.id", ondelete="CASCADE"),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    passport_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    certificate: Mapped[Certificate] = relationship(back_populates="individuals")

