"""
Conversion helpers between dataclasses and ORM models.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Optional

from models import (
    BankAccount,
    Deposit,
    GoldHolding,
    Individual,
    InsurancePolicy,
    Liability,
    MutualFund,
    NPSAccount,
    NetWorthData,
    PFAccount,
    PartnershipFirm,
    PostOfficeScheme,
    Property,
    Share,
    Vehicle,
)

from . import models as orm

DEFAULT_DOCUMENT_MIME = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


def _serialize_dataclass(data_obj: NetWorthData) -> str:
    """Return a JSON snapshot of the NetWorthData dataclass."""
    return json.dumps(asdict(data_obj), default=str)


def _build_individuals_display_name(data: NetWorthData) -> str:
    """
    Build a concise display name for the certificate list from the individuals.
    """
    if not data.individuals:
        return "Unnamed Individual"

    names = [ind.full_name.strip() for ind in data.individuals if ind.full_name.strip()]
    if not names:
        return "Unnamed Individual"

    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} & {names[1]}"
    # For 3 or more, show the first two and indicate how many more
    return f"{names[0]} & {names[1]} + {len(names) - 2} more"


def networth_to_certificate_model(
    data: NetWorthData,
    *,
    person_id: Optional[str] = None,
    document_bytes: Optional[bytes] = None,
    document_file_name: Optional[str] = None,
    document_mime_type: Optional[str] = None,
    extra_metadata: Optional[dict[str, Any]] = None,
) -> orm.Certificate:
    """
    Convert NetWorthData plus document payload into a Certificate ORM instance.
    """
    metadata_payload = extra_metadata or {}
    metadata_payload.setdefault("schema_version", "1.0")
    metadata_payload.setdefault("generated_notes", "Created via Streamlit UI")

    certificate = orm.Certificate(
        individual_name=_build_individuals_display_name(data),
        certificate_date=data.certificate_date,
        engagement_date=data.engagement_date,
        embassy_name=data.embassy_name,
        embassy_address=data.embassy_address,
        foreign_currency=data.foreign_currency,
        exchange_rate=data.exchange_rate,
        bank_accounts_notes=data.bank_accounts_notes or None,
        insurance_policies_notes=data.insurance_policies_notes or None,
        pf_accounts_notes=data.pf_accounts_notes or None,
        deposits_notes=data.deposits_notes or None,
        nps_accounts_notes=data.nps_accounts_notes or None,
        mutual_funds_notes=data.mutual_funds_notes or None,
        shares_notes=data.shares_notes or None,
        vehicles_notes=data.vehicles_notes or None,
        post_office_schemes_notes=data.post_office_schemes_notes or None,
        partnership_firms_notes=data.partnership_firms_notes or None,
        gold_holdings_notes=data.gold_holdings_notes or None,
        properties_notes=data.properties_notes or None,
        liabilities_notes=data.liabilities_notes or None,
        ca_firm_name=data.ca_firm_name,
        ca_frn=data.ca_frn,
        ca_partner_name=data.ca_partner_name,
        ca_membership_no=data.ca_membership_no,
        ca_designation=data.ca_designation,
        ca_place=data.ca_place,
        total_movable_assets_inr=data.total_movable_assets_inr,
        total_immovable_assets_inr=data.total_immovable_assets_inr,
        total_liabilities_inr=data.total_liabilities_inr,
        net_worth_inr=data.net_worth_inr,
        net_worth_foreign=data.net_worth_foreign,
        data_snapshot=_serialize_dataclass(data),
        metadata_json=json.dumps(metadata_payload),
        document_file_name=document_file_name,
        document_mime_type=document_mime_type or DEFAULT_DOCUMENT_MIME,
        document_file_size=len(document_bytes) if document_bytes else None,
        document_bytes=document_bytes,
        person_id=person_id,
    )

    # Individuals
    certificate.individuals = [
        orm.CertificateIndividualModel(
            full_name=item.full_name,
            passport_number=item.passport_number or None,
            address=item.address or None,
        )
        for item in data.individuals
    ]

    certificate.bank_accounts = [
        orm.BankAccountModel(
            holder_name=item.holder_name,
            account_number=item.account_number,
            bank_name=item.bank_name,
            balance_inr=item.balance_inr,
            statement_date=item.statement_date,
        )
        for item in data.bank_accounts
    ]
    certificate.insurance_policies = [
        orm.InsurancePolicyModel(
            holder_name=item.holder_name,
            policy_number=item.policy_number,
            amount_inr=item.amount_inr,
        )
        for item in data.insurance_policies
    ]
    certificate.pf_accounts = [
        orm.PFAccountModel(
            holder_name=item.holder_name,
            pf_account_number=item.pf_account_number,
            amount_inr=item.amount_inr,
        )
        for item in data.pf_accounts
    ]
    certificate.deposits = [
        orm.DepositModel(
            holder_name=item.holder_name,
            account_number=item.account_number,
            amount_inr=item.amount_inr,
        )
        for item in data.deposits
    ]
    certificate.nps_accounts = [
        orm.NPSAccountModel(
            owner_name=item.owner_name,
            pran_number=item.pran_number,
            amount_inr=item.amount_inr,
        )
        for item in data.nps_accounts
    ]
    certificate.mutual_funds = [
        orm.MutualFundModel(
            holder_name=item.holder_name,
            folio_number=item.folio_number,
            policy_name=item.policy_name,
            amount_inr=item.amount_inr,
        )
        for item in data.mutual_funds
    ]
    certificate.shares = [
        orm.ShareModel(
            company_name=item.company_name,
            num_shares=item.num_shares,
            market_price_inr=item.market_price_inr,
        )
        for item in data.shares
    ]
    certificate.vehicles = [
        orm.VehicleModel(
            vehicle_type=item.vehicle_type,
            make_model_year=item.make_model_year,
            registration_number=item.registration_number,
            market_value_inr=item.market_value_inr,
        )
        for item in data.vehicles
    ]
    certificate.post_office_schemes = [
        orm.PostOfficeSchemeModel(
            scheme_type=item.scheme_type,
            account_number=item.account_number,
            amount_inr=item.amount_inr,
        )
        for item in data.post_office_schemes
    ]
    certificate.partnership_firms = [
        orm.PartnershipFirmModel(
            firm_name=item.firm_name,
            partner_name=item.partner_name,
            holding_percentage=item.holding_percentage,
            capital_balance_inr=item.capital_balance_inr,
            valuation_date=item.valuation_date,
        )
        for item in data.partnership_firms
    ]
    certificate.gold_holdings = [
        orm.GoldHoldingModel(
            owner_name=item.owner_name,
            weight_grams=item.weight_grams,
            rate_per_10g=item.rate_per_10g,
            valuation_date=item.valuation_date,
            valuer_name=item.valuer_name,
        )
        for item in data.gold_holdings
    ]
    certificate.properties = [
        orm.PropertyModel(
            owner_name=item.owner_name,
            property_type=item.property_type,
            address=item.address,
            valuation_inr=item.valuation_inr,
            valuation_date=item.valuation_date,
            valuer_name=item.valuer_name,
        )
        for item in data.properties
    ]
    certificate.liabilities = [
        orm.LiabilityModel(
            description=item.description,
            amount_inr=item.amount_inr,
            details=item.details or None,
        )
        for item in data.liabilities
    ]

    return certificate


def _note_or_empty(value: Optional[str]) -> str:
    return value or ""


def certificate_to_networth_data(certificate: orm.Certificate) -> NetWorthData:
    """
    Hydrate a NetWorthData instance from a Certificate ORM entity.
    """
    individuals = [
        Individual(
            full_name=item.full_name,
            passport_number=item.passport_number or "",
            address=item.address or "",
        )
        for item in certificate.individuals
    ]

    networth = NetWorthData(
        certificate_date=certificate.certificate_date,
        engagement_date=certificate.engagement_date,
        embassy_name=certificate.embassy_name,
        embassy_address=certificate.embassy_address,
        individuals=individuals,
    )

    networth.foreign_currency = certificate.foreign_currency
    networth.exchange_rate = certificate.exchange_rate

    networth.bank_accounts = [
        BankAccount(
            holder_name=item.holder_name,
            account_number=item.account_number,
            bank_name=item.bank_name,
            balance_inr=item.balance_inr,
            statement_date=item.statement_date or "",
        )
        for item in certificate.bank_accounts
    ]
    networth.insurance_policies = [
        InsurancePolicy(
            holder_name=item.holder_name,
            policy_number=item.policy_number,
            amount_inr=item.amount_inr,
        )
        for item in certificate.insurance_policies
    ]
    networth.pf_accounts = [
        PFAccount(
            holder_name=item.holder_name,
            pf_account_number=item.pf_account_number,
            amount_inr=item.amount_inr,
        )
        for item in certificate.pf_accounts
    ]
    networth.deposits = [
        Deposit(
            holder_name=item.holder_name,
            account_number=item.account_number,
            amount_inr=item.amount_inr,
        )
        for item in certificate.deposits
    ]
    networth.nps_accounts = [
        NPSAccount(
            owner_name=item.owner_name,
            pran_number=item.pran_number,
            amount_inr=item.amount_inr,
        )
        for item in certificate.nps_accounts
    ]
    networth.mutual_funds = [
        MutualFund(
            holder_name=item.holder_name,
            folio_number=item.folio_number,
            policy_name=item.policy_name,
            amount_inr=item.amount_inr,
        )
        for item in certificate.mutual_funds
    ]
    networth.shares = [
        Share(
            company_name=item.company_name,
            num_shares=item.num_shares,
            market_price_inr=item.market_price_inr,
        )
        for item in certificate.shares
    ]
    networth.vehicles = [
        Vehicle(
            vehicle_type=item.vehicle_type,
            make_model_year=item.make_model_year,
            registration_number=item.registration_number,
            market_value_inr=item.market_value_inr,
        )
        for item in certificate.vehicles
    ]
    networth.post_office_schemes = [
        PostOfficeScheme(
            scheme_type=item.scheme_type,
            account_number=item.account_number,
            amount_inr=item.amount_inr,
        )
        for item in certificate.post_office_schemes
    ]
    networth.partnership_firms = [
        PartnershipFirm(
            firm_name=item.firm_name,
            partner_name=item.partner_name,
            holding_percentage=item.holding_percentage,
            capital_balance_inr=item.capital_balance_inr,
            valuation_date=item.valuation_date or "",
        )
        for item in certificate.partnership_firms
    ]
    networth.gold_holdings = [
        GoldHolding(
            owner_name=item.owner_name,
            weight_grams=item.weight_grams,
            rate_per_10g=item.rate_per_10g,
            valuation_date=item.valuation_date or "",
            valuer_name=item.valuer_name or "",
        )
        for item in certificate.gold_holdings
    ]
    networth.properties = [
        Property(
            owner_name=item.owner_name,
            property_type=item.property_type,
            address=item.address,
            valuation_inr=item.valuation_inr,
            valuation_date=item.valuation_date or "",
            valuer_name=item.valuer_name or "",
        )
        for item in certificate.properties
    ]
    networth.liabilities = [
        Liability(
            description=item.description,
            amount_inr=item.amount_inr,
            details=item.details or "",
        )
        for item in certificate.liabilities
    ]

    networth.bank_accounts_notes = _note_or_empty(certificate.bank_accounts_notes)
    networth.insurance_policies_notes = _note_or_empty(certificate.insurance_policies_notes)
    networth.pf_accounts_notes = _note_or_empty(certificate.pf_accounts_notes)
    networth.deposits_notes = _note_or_empty(certificate.deposits_notes)
    networth.nps_accounts_notes = _note_or_empty(certificate.nps_accounts_notes)
    networth.mutual_funds_notes = _note_or_empty(certificate.mutual_funds_notes)
    networth.shares_notes = _note_or_empty(certificate.shares_notes)
    networth.vehicles_notes = _note_or_empty(certificate.vehicles_notes)
    networth.post_office_schemes_notes = _note_or_empty(certificate.post_office_schemes_notes)
    networth.partnership_firms_notes = _note_or_empty(certificate.partnership_firms_notes)
    networth.gold_holdings_notes = _note_or_empty(certificate.gold_holdings_notes)
    networth.properties_notes = _note_or_empty(certificate.properties_notes)
    networth.liabilities_notes = _note_or_empty(certificate.liabilities_notes)

    return networth

