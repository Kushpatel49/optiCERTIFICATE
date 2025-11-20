"""
Test data generation utilities for Net Worth Certificate Generator
"""

import datetime
import streamlit as st

from models import (
    BankAccount,
    InsurancePolicy,
    PFAccount,
    Deposit,
    NPSAccount,
    MutualFund,
    Share,
    Vehicle,
    PostOfficeScheme,
    PartnershipFirm,
    GoldHolding,
    Property,
    Liability,
    Individual,
    NetWorthData,
)


def auto_fill_test_data():
    """Auto-fill all form fields with comprehensive test data for testing"""
    # Initialize session state data
    st.session_state.data = NetWorthData(
        certificate_date=datetime.date.today().strftime("%d/%m/%Y"),
        engagement_date=datetime.date.today().strftime("%d/%m/%Y"),
        embassy_name="Canadian High Commission",
        embassy_address="7/8 Shantipath, Chanakyapuri\nNew Delhi - 110021",
        individuals=[
            Individual(
                full_name="Bharatkumar Dhulabhai Patel",
                passport_number="A12345678",
                address="29/B, Ratnamani Tenaments, Ahmedabad, Gujarat - 380001",
            )
        ],
        foreign_currency="CAD",
        exchange_rate=63.34
    )

    # Bank Accounts
    st.session_state.data.bank_accounts = [
        BankAccount(
            holder_name="Bharatkumar Dhulabhai Patel",
            account_number="10733415306",
            bank_name="State Bank of India",
            balance_inr=1078118.46,
            statement_date=datetime.date.today().strftime("%d/%m/%Y")
        ),
        BankAccount(
            holder_name="Bharatkumar Dhulabhai Patel",
            account_number="20093766850",
            bank_name="HDFC Bank",
            balance_inr=385989.69,
            statement_date=datetime.date.today().strftime("%d/%m/%Y")
        )
    ]

    # Insurance Policies
    st.session_state.data.insurance_policies = [
        InsurancePolicy(
            holder_name="Bharatkumar Dhulabhai Patel",
            policy_number="71234567890",
            amount_inr=253618.00
        )
    ]

    # P.F. Accounts
    st.session_state.data.pf_accounts = [
        PFAccount(
            holder_name="Bharatkumar Dhulabhai Patel",
            pf_account_number="GJ/AMD/12345/678",
            amount_inr=1850652.00
        )
    ]

    # Deposits
    st.session_state.data.deposits = [
        Deposit(
            holder_name="Bharatkumar Dhulabhai Patel",
            account_number="FD123456789",
            amount_inr=1000000.00
        )
    ]

    # NPS Accounts
    st.session_state.data.nps_accounts = [
        NPSAccount(
            owner_name="Bharatkumar Dhulabhai Patel",
            pran_number="110021379979",
            amount_inr=2578706.52
        )
    ]

    # Mutual Funds
    st.session_state.data.mutual_funds = [
        MutualFund(
            holder_name="Bharatkumar Dhulabhai Patel",
            folio_number="34521763/59",
            policy_name="HDFC Flexi Cap Fund",
            amount_inr=126662.88
        )
    ]

    # Shares
    st.session_state.data.shares = [
        Share(
            company_name="Reliance Industries Ltd",
            num_shares=100,
            market_price_inr=2450.00
        ),
        Share(
            company_name="TCS Ltd",
            num_shares=50,
            market_price_inr=3200.00
        )
    ]

    # Vehicles
    st.session_state.data.vehicles = [
        Vehicle(
            vehicle_type="Car",
            make_model_year="Toyota Innova Crysta 2020",
            registration_number="GJ01AB1234",
            market_value_inr=1500000.00
        )
    ]

    # Post Office Schemes
    st.session_state.data.post_office_schemes = [
        PostOfficeScheme(
            scheme_type="National Savings Certificate (NSC)",
            account_number="NSC123456789",
            amount_inr=500000.00
        )
    ]

    # Partnership Firms
    st.session_state.data.partnership_firms = [
        PartnershipFirm(
            firm_name="Patel Brothers Trading Co.",
            partner_name="Bharatkumar Dhulabhai Patel",
            holding_percentage=33.33,
            capital_balance_inr=2000000.00,
            valuation_date=datetime.date.today().strftime("%d/%m/%Y")
        )
    ]

    # Gold Holdings
    st.session_state.data.gold_holdings = [
        GoldHolding(
            owner_name="Bharatkumar Dhulabhai Patel",
            weight_grams=399.570,
            rate_per_10g=109500,
            valuation_date=datetime.date.today().strftime("%d/%m/%Y"),
            valuer_name="Approved Valuer - Ahmedabad"
        )
    ]

    # Properties
    st.session_state.data.properties = [
        Property(
            owner_name="Bharatkumar Dhulabhai Patel",
            property_type="Residential House",
            address="29/B, Ratnamani Tenaments, Survey No. 123, Ahmedabad",
            valuation_inr=1260000,
            valuation_date=datetime.date.today().strftime("%d/%m/%Y"),
            valuer_name="Approved Valuer - Ahmedabad"
        ),
        Property(
            owner_name="Bharatkumar Dhulabhai Patel",
            property_type="Commercial Property",
            address="Shop No. 5, Commercial Complex, SG Highway, Ahmedabad",
            valuation_inr=2500000,
            valuation_date=datetime.date.today().strftime("%d/%m/%Y"),
            valuer_name="Approved Valuer - Ahmedabad"
        )
    ]

    # Liabilities
    st.session_state.data.liabilities = [
        Liability(
            description="Home Loan",
            amount_inr=800000.00,
            details="Housing loan from SBI for residential property"
        )
    ]

    print("✅ Test data auto-filled successfully!")
    print(f"📊 Total Assets: ₹{st.session_state.data.total_movable_assets_inr + st.session_state.data.total_immovable_assets_inr:,.2f}")
    print(f"💰 Net Worth: ₹{st.session_state.data.net_worth_inr:,.2f}")
    print("🎯 Ready to generate certificate on Summary page!")

