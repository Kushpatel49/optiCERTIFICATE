"""
Data models for Net Worth Certificate Generator
"""

import streamlit as st
from dataclasses import dataclass, field
from typing import List
from config import DEFAULT_EXCHANGE_RATE


def get_exchange_rate() -> float:
    """Get current exchange rate from session state or default"""
    return st.session_state.get('exchange_rate', DEFAULT_EXCHANGE_RATE)


@dataclass
class BankAccount:
    holder_name: str
    account_number: str
    bank_name: str
    balance_inr: float
    statement_date: str = ""
    
    @property
    def balance_foreign(self) -> float:
        return self.balance_inr / get_exchange_rate()


@dataclass
class InsurancePolicy:
    holder_name: str
    policy_number: str
    amount_inr: float
    
    @property
    def amount_foreign(self) -> float:
        return self.amount_inr / get_exchange_rate()


@dataclass
class PFAccount:
    holder_name: str
    pf_account_number: str
    amount_inr: float
    
    @property
    def amount_foreign(self) -> float:
        return self.amount_inr / get_exchange_rate()


@dataclass
class Deposit:
    holder_name: str
    account_number: str
    amount_inr: float
    
    @property
    def amount_foreign(self) -> float:
        return self.amount_inr / get_exchange_rate()


@dataclass
class NPSAccount:
    owner_name: str
    pran_number: str
    amount_inr: float

    @property
    def amount_foreign(self) -> float:
        return self.amount_inr / get_exchange_rate()


@dataclass
class MutualFund:
    holder_name: str
    folio_number: str
    policy_name: str
    amount_inr: float

    @property
    def amount_foreign(self) -> float:
        return self.amount_inr / get_exchange_rate()


@dataclass
class Share:
    company_name: str
    num_shares: int
    market_price_inr: float

    @property
    def amount_inr(self) -> float:
        return self.num_shares * self.market_price_inr

    @property
    def amount_foreign(self) -> float:
        return self.amount_inr / get_exchange_rate()


@dataclass
class Vehicle:
    vehicle_type: str
    make_model_year: str
    registration_number: str
    market_value_inr: float

    @property
    def amount_foreign(self) -> float:
        return self.market_value_inr / get_exchange_rate()


@dataclass
class PostOfficeScheme:
    scheme_type: str
    account_number: str
    amount_inr: float
    
    @property
    def amount_foreign(self) -> float:
        return self.amount_inr / get_exchange_rate()


@dataclass
class PartnershipFirm:
    firm_name: str
    partner_name: str
    holding_percentage: float
    capital_balance_inr: float
    valuation_date: str

    @property
    def amount_foreign(self) -> float:
        return self.capital_balance_inr / get_exchange_rate()


@dataclass
class GoldHolding:
    owner_name: str
    weight_grams: float
    rate_per_10g: float
    valuation_date: str = ""
    valuer_name: str = ""
    
    @property
    def amount_inr(self) -> float:
        return (self.weight_grams / 10) * self.rate_per_10g
    
    @property
    def amount_foreign(self) -> float:
        return self.amount_inr / get_exchange_rate()


@dataclass
class Property:
    owner_name: str
    property_type: str
    address: str
    valuation_inr: float
    valuation_date: str = ""
    valuer_name: str = ""
    
    @property
    def valuation_foreign(self) -> float:
        return self.valuation_inr / get_exchange_rate()


@dataclass
class Liability:
    description: str
    amount_inr: float
    details: str = ""


@dataclass
class Individual:
    """
    Represents a single individual for whom the certificate is being issued.
    """

    full_name: str
    passport_number: str = ""
    address: str = ""


@dataclass
class NetWorthData:
    # Personal / contextual details
    certificate_date: str
    engagement_date: str
    embassy_name: str
    embassy_address: str

    # One or more individuals covered by this certificate
    individuals: List[Individual] = field(default_factory=list)

    foreign_currency: str = "CAD"
    exchange_rate: float = DEFAULT_EXCHANGE_RATE
    
    # Assets
    bank_accounts: List[BankAccount] = field(default_factory=list)
    insurance_policies: List[InsurancePolicy] = field(default_factory=list)
    pf_accounts: List[PFAccount] = field(default_factory=list)
    deposits: List[Deposit] = field(default_factory=list)
    nps_accounts: List[NPSAccount] = field(default_factory=list)
    mutual_funds: List[MutualFund] = field(default_factory=list)
    shares: List[Share] = field(default_factory=list)
    vehicles: List[Vehicle] = field(default_factory=list)
    post_office_schemes: List[PostOfficeScheme] = field(default_factory=list)
    partnership_firms: List[PartnershipFirm] = field(default_factory=list)
    gold_holdings: List[GoldHolding] = field(default_factory=list)
    properties: List[Property] = field(default_factory=list)
    
    # Liabilities
    liabilities: List[Liability] = field(default_factory=list)
    
    # Notes for each category
    bank_accounts_notes: str = ""
    insurance_policies_notes: str = ""
    pf_accounts_notes: str = ""
    deposits_notes: str = ""
    nps_accounts_notes: str = ""
    mutual_funds_notes: str = ""
    shares_notes: str = ""
    vehicles_notes: str = ""
    post_office_schemes_notes: str = ""
    partnership_firms_notes: str = ""
    gold_holdings_notes: str = ""
    properties_notes: str = ""
    liabilities_notes: str = ""
    
    # CA Details (Pre-filled)
    ca_firm_name: str = "Patel Parekh & Associates"
    ca_frn: str = "154335W"
    ca_partner_name: str = "CA HARSH B PATEL"
    ca_membership_no: str = "600794"
    ca_designation: str = "Partner"
    ca_place: str = "Vijapur"
    
    @property
    def total_bank_balance_inr(self) -> float:
        return sum(acc.balance_inr for acc in self.bank_accounts)
    
    @property
    def total_bank_balance_foreign(self) -> float:
        return self.total_bank_balance_inr / self.exchange_rate
    
    @property
    def total_insurance_inr(self) -> float:
        return sum(pol.amount_inr for pol in self.insurance_policies)
    
    @property
    def total_insurance_foreign(self) -> float:
        return self.total_insurance_inr / self.exchange_rate
    
    @property
    def total_pf_accounts_inr(self) -> float:
        return sum(acc.amount_inr for acc in self.pf_accounts)
    
    @property
    def total_pf_accounts_foreign(self) -> float:
        return self.total_pf_accounts_inr / self.exchange_rate

    @property
    def total_deposits_inr(self) -> float:
        return sum(dep.amount_inr for dep in self.deposits)
    
    @property
    def total_deposits_foreign(self) -> float:
        return self.total_deposits_inr / self.exchange_rate
    
    @property
    def total_nps_inr(self) -> float:
        return sum(nps.amount_inr for nps in self.nps_accounts)

    @property
    def total_nps_foreign(self) -> float:
        return self.total_nps_inr / self.exchange_rate

    @property
    def total_mutual_funds_inr(self) -> float:
        return sum(mf.amount_inr for mf in self.mutual_funds)

    @property
    def total_mutual_funds_foreign(self) -> float:
        return self.total_mutual_funds_inr / self.exchange_rate

    @property
    def total_shares_inr(self) -> float:
        return sum(s.amount_inr for s in self.shares)

    @property
    def total_shares_foreign(self) -> float:
        return self.total_shares_inr / self.exchange_rate

    @property
    def total_vehicles_inr(self) -> float:
        return sum(v.market_value_inr for v in self.vehicles)

    @property
    def total_vehicles_foreign(self) -> float:
        return self.total_vehicles_inr / self.exchange_rate

    @property
    def total_post_office_inr(self) -> float:
        return sum(p.amount_inr for p in self.post_office_schemes)

    @property
    def total_post_office_foreign(self) -> float:
        return self.total_post_office_inr / self.exchange_rate
    
    @property
    def total_partnership_firms_inr(self) -> float:
        return sum(f.capital_balance_inr for f in self.partnership_firms)

    @property
    def total_partnership_firms_foreign(self) -> float:
        return self.total_partnership_firms_inr / self.exchange_rate
    
    @property
    def total_gold_inr(self) -> float:
        return sum(gold.amount_inr for gold in self.gold_holdings)
    
    @property
    def total_gold_foreign(self) -> float:
        return self.total_gold_inr / self.exchange_rate
    
    @property
    def total_movable_assets_inr(self) -> float:
        return (self.total_bank_balance_inr + 
                self.total_insurance_inr + 
                self.total_pf_accounts_inr + 
                self.total_deposits_inr +
                self.total_nps_inr +
                self.total_mutual_funds_inr +
                self.total_shares_inr +
                self.total_vehicles_inr +
                self.total_post_office_inr +
                self.total_partnership_firms_inr +
                self.total_gold_inr)
    
    @property
    def total_movable_assets_foreign(self) -> float:
        return self.total_movable_assets_inr / self.exchange_rate
    
    @property
    def total_immovable_assets_inr(self) -> float:
        return sum(prop.valuation_inr for prop in self.properties)
    
    @property
    def total_immovable_assets_foreign(self) -> float:
        return self.total_immovable_assets_inr / self.exchange_rate
    
    @property
    def total_liabilities_inr(self) -> float:
        return sum(liab.amount_inr for liab in self.liabilities)
    
    @property
    def total_liabilities_foreign(self) -> float:
        if self.exchange_rate == 0:
            return 0.0
        return self.total_liabilities_inr / self.exchange_rate
    
    @property
    def net_worth_inr(self) -> float:
        return self.total_movable_assets_inr + self.total_immovable_assets_inr - self.total_liabilities_inr
    
    @property
    def net_worth_foreign(self) -> float:
        return self.net_worth_inr / self.exchange_rate

