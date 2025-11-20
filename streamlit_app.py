"""
Net Worth Certificate Generator - Main Streamlit Application
"""

import streamlit as st  # type: ignore[import-not-found]
import datetime
import io
import base64
import json
from typing import List

# Import from organized modules
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
from generators import generate_networth_certificate
from utils import fetch_exchange_rate, auto_fill_test_data
from config import CA_PARTNERS, SUPPORTED_CURRENCIES, DEFAULT_EXCHANGE_RATE
from ui.styling import LIGHT_THEME_CSS

try:
    from db.engine import init_db
    from db.repository import (
        CertificateSummary,
        RepositoryError,
        get_certificate_detail,
        list_certificates_for_person,
        list_persons,
        list_recent_certificates,
        save_certificate,
        save_person,
    )

    DB_AVAILABLE = True
    DB_IMPORT_ERROR: Exception | None = None
except Exception as db_import_exc:
    DB_AVAILABLE = False
    DB_IMPORT_ERROR = db_import_exc

    class RepositoryError(RuntimeError):  # type: ignore[override]
        """Fallback RepositoryError when DB layer is unavailable."""

        pass


def ensure_database_initialized() -> None:
    """Ensure tables exist when using the local SQLite fallback."""
    if not DB_AVAILABLE:
        return
    if st.session_state.get("_db_initialized"):
        return
    try:
        init_db()
        st.session_state["_db_initialized"] = True
    except Exception as exc:  # pragma: no cover - defensive path
        st.session_state["_db_initialized"] = False
        st.session_state["_db_init_error"] = str(exc)


def load_certificate_into_session(certificate_id: str) -> None:
    """Load a stored certificate into the active Streamlit session."""
    if not DB_AVAILABLE:
        return
    try:
        detail = get_certificate_detail(certificate_id)
    except Exception as exc:  # pragma: no cover - runtime defensive
        st.sidebar.error(f"Failed to load certificate: {exc}")
        return

    if detail is None:
        st.sidebar.warning("Selected certificate could not be found.")
        return

    st.session_state.data = detail.data
    st.session_state.previous_currency = detail.data.foreign_currency
    st.session_state.exchange_rate = detail.data.exchange_rate
    st.session_state.download_completed = False
    st.session_state["_loaded_certificate_id"] = certificate_id
    st.session_state["_show_load_notice"] = True
    st.session_state.selected_certificate_id = certificate_id
    if detail.person_id:
        st.session_state.selected_person_id = detail.person_id
    st.rerun()


def create_empty_networth_data() -> NetWorthData:
    """Create a fresh NetWorthData object with today's dates and one blank individual."""
    today_str = datetime.date.today().strftime("%d/%m/%Y")
    return NetWorthData(
        certificate_date=today_str,
        engagement_date=today_str,
        embassy_name="",
        embassy_address="",
        individuals=[
            Individual(full_name="", passport_number="", address="")
        ],
    )


CLIENT_DROPDOWN_PLACEHOLDER = "-- Select Client --"
CERTIFICATE_DROPDOWN_PLACEHOLDER = "-- Select Certificate --"


def render_clients_sidebar() -> None:
    """Render sidebar controls for managing clients and their certificates."""
    sidebar = st.sidebar
    sidebar.header("Clients & Certificates")

    if not DB_AVAILABLE:
        sidebar.info("Database storage is not configured yet.")
        if DB_IMPORT_ERROR:
            sidebar.caption(f"{DB_IMPORT_ERROR}")
        return

    ensure_database_initialized()
    if st.session_state.get("_db_initialized") is False:
        sidebar.warning("Database initialization failed. Check configuration.")
        error_text = st.session_state.get("_db_init_error")
        if error_text:
            sidebar.caption(error_text)
        return

    if st.session_state.pop("_show_person_notice", False):
        sidebar.success("Client created successfully.")

    try:
        persons = list_persons()
    except Exception as exc:  # pragma: no cover - runtime defensive
        sidebar.warning("Unable to fetch clients.")
        sidebar.caption(str(exc))
        persons = []

    selected_person_id = st.session_state.get("selected_person_id")
    person_label_map = {CLIENT_DROPDOWN_PLACEHOLDER: None}
    person_options: List[str] = [CLIENT_DROPDOWN_PLACEHOLDER]
    default_person_index = 0

    for idx, person in enumerate(persons, start=1):
        label = person.display_name
        person_label_map[label] = person
        person_options.append(label)
        if selected_person_id == person.id:
            default_person_index = idx

    selection = sidebar.selectbox(
        "Select client",
        person_options,
        index=default_person_index,
        key="client_selectbox",
    )

    selected_person = person_label_map.get(selection)

    if selected_person is None:
        st.session_state.selected_person_id = None
    else:
        st.session_state.selected_person_id = selected_person.id
        if selected_person.email:
            sidebar.caption(f"Email: {selected_person.email}")
        if selected_person.phone_number:
            sidebar.caption(f"Phone: {selected_person.phone_number}")

    reset_fields = st.session_state.pop("_reset_client_fields", False)
    if reset_fields:
        for key in ("new_client_name", "new_client_email", "new_client_phone"):
            st.session_state.pop(key, None)

    sidebar.markdown("---")
    sidebar.subheader("Add New Client")
    new_name = sidebar.text_input("Client Name", key="new_client_name")
    new_email = sidebar.text_input("Email (optional)", key="new_client_email")
    new_phone = sidebar.text_input("Phone (optional)", key="new_client_phone")

    if sidebar.button("Create Client", key="create_client_button", use_container_width=True):
        name = (new_name or "").strip()
        email = (new_email or "").strip() or None
        phone = (new_phone or "").strip() or None

        if not name:
            sidebar.warning("Enter a client name before creating.")
        else:
            try:
                person = save_person(
                    display_name=name,
                    email=email,
                    phone_number=phone,
                )
                st.session_state.selected_person_id = person.id
                st.session_state.selected_certificate_id = None
                st.session_state["_show_person_notice"] = True
                st.session_state["_reset_client_fields"] = True
                st.rerun()
            except RepositoryError as exc:
                sidebar.error(f"Could not create client: {exc}")
            except Exception as exc:  # pragma: no cover - defensive
                sidebar.error(f"Unexpected error creating client: {exc}")

    sidebar.markdown("---")
    sidebar.subheader("Certificates")

    try:
        if st.session_state.get("selected_person_id"):
            summaries = list_certificates_for_person(
                st.session_state["selected_person_id"], limit=20
            )
        else:
            summaries = list_recent_certificates(limit=10)
    except Exception as exc:  # pragma: no cover - runtime defensive
        sidebar.warning("Unable to fetch certificates.")
        sidebar.caption(str(exc))
        return

    if st.session_state.get("selected_person_id") and not summaries:
        sidebar.caption("No certificates saved for this client yet.")
    elif not summaries:
        sidebar.caption("No certificates saved yet.")

    cert_label_map: dict[str, CertificateSummary] = {}
    cert_options: List[str] = [CERTIFICATE_DROPDOWN_PLACEHOLDER]
    default_cert_index = 0
    selected_certificate_id = st.session_state.get("selected_certificate_id")

    for idx, summary in enumerate(summaries, start=1):
        base_label = f"{summary.certificate_date} – ₹{summary.net_worth_inr:,.0f}"
        if st.session_state.get("selected_person_id"):
            label = base_label
        else:
            label = f"{summary.individual_name} — {base_label}"
        cert_label_map[label] = summary
        cert_options.append(label)
        if selected_certificate_id == summary.id:
            default_cert_index = idx

    selection = sidebar.selectbox(
        "Select certificate",
        cert_options,
        index=default_cert_index,
        key="certificate_selectbox",
    )

    selected_summary = cert_label_map.get(selection)

    if selected_summary:
        st.session_state.selected_certificate_id = selected_summary.id
        sidebar.caption(f"Net Worth (INR): ₹{selected_summary.net_worth_inr:,.2f}")
        sidebar.caption(f"Created: {selected_summary.created_at}")

    if selected_summary and sidebar.button(
        "Load Certificate",
        key=f"load_certificate_button_{selected_summary.id}",
        use_container_width=True,
    ):
        load_certificate_into_session(selected_summary.id)

# ==================== MAIN APPLICATION ====================

def main():
    st.set_page_config(page_title="Net Worth Certificate Generator", layout="wide", page_icon="📄")

    render_clients_sidebar()

    if st.session_state.pop("_show_load_notice", False):
        st.success("✅ Loaded saved certificate data.")
    
    # Check for test mode parameter
    query_params = st.query_params
    test_mode = query_params.get('test', 'false').lower() == 'true'

    # Auto-fill test data if in test mode
    if test_mode and 'data' not in st.session_state:
        auto_fill_test_data()

        # Auto-navigate to summary page in test mode
        if test_mode:
            st.markdown("""
            <script>
                // Auto-navigate to Summary tab
                setTimeout(() => {
                    const tabs = document.querySelectorAll('[data-baseweb="tab"]');
                    if (tabs.length > 0) {
                        tabs[tabs.length - 1].click(); // Click last tab (Summary)
                    }
                }, 1000); // Wait 1 second for data to load
            </script>
            """, unsafe_allow_html=True)
    elif not test_mode and DB_AVAILABLE:
        # When a client is selected, automatically load their most recent certificate
        # into the form the first time that client is chosen in this session.
        selected_person_id = st.session_state.get("selected_person_id")
        last_person_for_data = st.session_state.get("_last_person_for_data")

        if selected_person_id and selected_person_id != last_person_for_data:
            try:
                summaries = list_certificates_for_person(selected_person_id, limit=1)
            except Exception as exc:  # pragma: no cover - runtime defensive
                st.sidebar.warning("Unable to auto-load last certificate for this client.")
                st.sidebar.caption(str(exc))
                st.session_state["_last_person_for_data"] = selected_person_id
            else:
                st.session_state["_last_person_for_data"] = selected_person_id
                if summaries:
                    latest = summaries[0]
                    load_certificate_into_session(latest.id)
                else:
                    # No certificates yet for this client – start with a clean form.
                    st.session_state.data = create_empty_networth_data()
        elif selected_person_id is None and last_person_for_data is not None:
            # Client deselected – reset to a clean form once.
            st.session_state["_last_person_for_data"] = None
            st.session_state.data = create_empty_networth_data()

    # Apply custom CSS
    st.markdown(f"<style>{LIGHT_THEME_CSS}</style>", unsafe_allow_html=True)
    
    # Add script to restore tab and scroll position on page load/rerun
    restore_state_js = """
    <script>
    (function() {
        function restoreState() {
            try {
                const mainWindow = window.parent !== window ? window.parent : window;
                const mainDoc = mainWindow.document;
                
                // Restore scroll position
                const savedScroll = mainWindow.sessionStorage.getItem('preserve_scroll');
                if (savedScroll && mainWindow.scrollTo) {
                    const pos = parseInt(savedScroll);
                    mainWindow.scrollTo(0, pos);
                }
                
                // Restore active tab
                const savedTab = mainWindow.sessionStorage.getItem('preserve_tab');
                if (savedTab) {
                    const tabs = mainDoc.querySelectorAll('[data-baseweb="tab"], [role="tab"]');
                    const tabIndex = parseInt(savedTab);
                    if (tabs.length > tabIndex) {
                        tabs[tabIndex].click();
                    } else {
                        // Fallback: find by text
                        const tabLabels = mainDoc.querySelectorAll('[data-baseweb="tab"]');
                        for (let tab of tabLabels) {
                            const text = tab.textContent || tab.innerText || '';
                            if (text.includes('Summary') || text.includes('Generate')) {
                                tab.click();
                                break;
                            }
                        }
                    }
                }
            } catch (e) {
                console.error('State restore error:', e);
            }
        }
        
        // Try multiple times to ensure DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', restoreState);
        } else {
            setTimeout(restoreState, 100);
            setTimeout(restoreState, 300);
            setTimeout(restoreState, 600);
        }
    })();
    </script>
    """
    # Use components.html to ensure script executes
    st.components.v1.html(restore_state_js, height=0)

    # Enhanced branding with optiCERTIFICATE logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Logo.png", use_column_width='auto')

    st.markdown("---")
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = NetWorthData(
            certificate_date=datetime.date.today().strftime("%d/%m/%Y"),
            engagement_date=datetime.date.today().strftime("%d/%m/%Y"),
            embassy_name="",
            embassy_address="",
            individuals=[
                Individual(full_name="", passport_number="", address="")
            ],
        )
    
    # For forward compatibility: ensure new fields exist on older session state objects
    new_fields = {
        'pf_accounts': [], 'deposits': [], 'nps_accounts': [], 'mutual_funds': [],
        'shares': [], 'vehicles': [], 'post_office_schemes': [], 'partnership_firms': [],
        'bank_accounts_notes': '', 'insurance_policies_notes': '', 'pf_accounts_notes': '',
        'deposits_notes': '', 'nps_accounts_notes': '', 'mutual_funds_notes': '',
        'shares_notes': '', 'vehicles_notes': '', 'post_office_schemes_notes': '',
        'partnership_firms_notes': '', 'gold_holdings_notes': '', 'properties_notes': '',
        'liabilities_notes': '',
        'individuals': [],
    }
    for field, default_value in new_fields.items():
        if not hasattr(st.session_state.data, field):
            setattr(st.session_state.data, field, default_value)
    
    # Tabs for different sections
    tabs = st.tabs([
        "📋 Basic Info", 
        "🏦 Bank Accounts", 
        "🛡️ Insurance", 
        "📈 P.F. Accounts",
        "💰 Deposits",
        "📊 NPS",
        "💼 Mutual Funds",
        "📈 Shares",
        "🚗 Vehicles",
        "📮 Post Office",
        "🤝 Partnership Firms",
        "💎 Gold/Valuables", 
        "🏠 Properties", 
        "💳 Liabilities",
        "📊 Summary & Generate"
    ])
    
    # Tab 1: Basic Information
    with tabs[0]:
        st.header("Basic Information")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Individuals")

            # Ensure we always have at least one individual entry
            if not getattr(st.session_state.data, "individuals", None):
                st.session_state.data.individuals = [
                    Individual(full_name="", passport_number="", address="")
                ]

            # Render each individual in an expander with editable fields
            for idx, individual in enumerate(st.session_state.data.individuals):
                expanded = len(st.session_state.data.individuals) == 1
                with st.expander(f"Individual {idx + 1}", expanded=expanded):
                    name = st.text_input(
                        "Full Name *",
                        value=individual.full_name,
                        key=f"individual_{idx}_name",
                    )
                    passport = st.text_input(
                        "Passport Number *",
                        value=individual.passport_number,
                        key=f"individual_{idx}_passport",
                        help="Passport number will be displayed after the name in the certificate",
                    )
                    address = st.text_area(
                        "Address *",
                        value=individual.address,
                        height=100,
                        key=f"individual_{idx}_address",
                    )

                    individual.full_name = name
                    individual.passport_number = passport
                    individual.address = address

                    if len(st.session_state.data.individuals) > 1:
                        if st.button(
                            "🗑️ Remove Individual",
                            key=f"remove_individual_{idx}",
                            use_container_width=True,
                        ):
                            st.session_state.data.individuals.pop(idx)
                            st.rerun()

            if st.button(
                "➕ Add Another Individual",
                key="add_individual_button",
                use_container_width=True,
            ):
                st.session_state.data.individuals.append(
                    Individual(full_name="", passport_number="", address="")
                )
                st.rerun()

            st.subheader("Certificate Dates")
            cert_date = st.date_input("Certificate Date", value=datetime.date.today())
            st.session_state.data.certificate_date = cert_date.strftime("%d/%m/%Y")
            
            eng_date = st.date_input("Engagement Letter Date", value=datetime.date.today())
            st.session_state.data.engagement_date = eng_date.strftime("%d/%m/%Y")
        
        with col2:
            st.subheader("Embassy/Consulate Details")
            st.session_state.data.embassy_name = st.text_input(
                "Embassy/Consulate Name *", 
                value=st.session_state.data.embassy_name,
                key="emb_name"
            )
            st.session_state.data.embassy_address = st.text_area(
                "Embassy Address *", 
                value=st.session_state.data.embassy_address,
                height=100,
                key="emb_addr"
            )
            
            st.subheader("Currency Settings")
            
            # Track previous currency to detect changes
            if 'previous_currency' not in st.session_state:
                st.session_state.previous_currency = st.session_state.data.foreign_currency
            
            # Currency selection
            current_currency = st.session_state.data.foreign_currency
            default_index = SUPPORTED_CURRENCIES.index(current_currency) if current_currency in SUPPORTED_CURRENCIES else 0
            
            selected_currency = st.selectbox(
                "Foreign Currency",
                SUPPORTED_CURRENCIES,
                index=default_index,
                key="currency_selectbox"
            )
            st.session_state.data.foreign_currency = selected_currency
            
            # Auto-fetch exchange rate when currency changes
            col1_rate, col2_rate = st.columns([3, 1])
            
            with col1_rate:
                # Check if currency changed
                currency_changed = st.session_state.previous_currency != selected_currency
                
                # Initialize exchange rate if not set
                if not hasattr(st.session_state.data, 'exchange_rate') or st.session_state.data.exchange_rate == 0:
                    st.session_state.data.exchange_rate = DEFAULT_EXCHANGE_RATE
                
                # Auto-fetch when currency changes
                if currency_changed:
                    # Fetch real-time exchange rate
                    with st.spinner(f"Fetching exchange rate for {selected_currency}..."):
                        fetched_rate = fetch_exchange_rate(selected_currency)
                        if fetched_rate:
                            st.session_state.data.exchange_rate = fetched_rate
                            st.session_state.previous_currency = selected_currency
                            st.success(f"Exchange rate updated: {fetched_rate} INR = 1 {selected_currency}")
                        else:
                            st.info(f"Using current rate: {st.session_state.data.exchange_rate} INR = 1 {selected_currency}")
                
                # Exchange rate input (editable)
                st.session_state.data.exchange_rate = st.number_input(
                    f"Exchange Rate (INR to 1 {selected_currency})",
                    min_value=0.01,
                    value=st.session_state.data.exchange_rate,
                    step=0.01,
                    format="%.2f",
                    key="exchange_rate_input"
                )
            
            with col2_rate:
                st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                if st.button("🔄 Refresh", help="Fetch latest exchange rate", key="refresh_rate_btn", use_container_width=True):
                    with st.spinner(f"Fetching latest rate for {selected_currency}..."):
                        fetched_rate = fetch_exchange_rate(selected_currency)
                        if fetched_rate:
                            st.session_state.data.exchange_rate = fetched_rate
                            st.session_state.previous_currency = selected_currency
                            st.rerun()
                        else:
                            st.warning("Could not fetch rate. Please enter manually.")
            
            st.session_state.exchange_rate = st.session_state.data.exchange_rate
        
        st.markdown("---")
        st.subheader("Chartered Accountant Details")
        
        col1_ca, col2_ca = st.columns(2)
        with col1_ca:
            selected_ca_name = st.selectbox(
                "Select Signing Partner",
                options=list(CA_PARTNERS.keys()),
                key="ca_name_select"
            )
            # Update session state with selected CA details
            st.session_state.data.ca_partner_name = selected_ca_name
            st.session_state.data.ca_membership_no = CA_PARTNERS[selected_ca_name]["membership_no"]

        with col2_ca:
            st.info(f"""
            **Firm:** {st.session_state.data.ca_firm_name}
            **FRN:** {st.session_state.data.ca_frn}
            """)

    # Tab 2: Bank Accounts
    with tabs[1]:
        st.header("Bank Accounts")
        
        st.subheader("Add New Bank Account")
        with st.form("bank_account_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                holder_name = st.text_input("Account Holder Name")
                account_number = st.text_input("Account Number")
            with col2:
                bank_name = st.text_input("Bank Name")
                balance = st.number_input("Balance (INR)", min_value=0.0, step=1000.0, format="%.2f")
            
            statement_date = st.date_input("Statement Date", value=datetime.date.today())
            
            if st.form_submit_button("➕ Add Bank Account"):
                if holder_name and account_number and bank_name:
                    new_account = BankAccount(
                        holder_name=holder_name,
                        account_number=account_number,
                        bank_name=bank_name,
                        balance_inr=balance,
                        statement_date=statement_date.strftime("%d/%m/%Y")
                    )
                    st.session_state.data.bank_accounts.append(new_account)
                    st.success("✅ Bank account added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.subheader("Current Bank Accounts")
        if st.session_state.data.bank_accounts:
            for idx, acc in enumerate(st.session_state.data.bank_accounts):
                with st.expander(f"Account {idx+1}: {acc.bank_name} - {acc.account_number}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Holder:** {acc.holder_name}")
                        st.write(f"**Bank:** {acc.bank_name}")
                    with col2:
                        st.write(f"**Balance (INR):** ₹{acc.balance_inr:,.2f}")
                        st.write(f"**Balance ({st.session_state.data.foreign_currency}):** {acc.balance_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_bank_{idx}"):
                            st.session_state.data.bank_accounts.pop(idx)
                            st.rerun()
            
            st.metric("Total Bank Balance (INR)", f"₹{st.session_state.data.total_bank_balance_inr:,.2f}")
        else:
            st.info("No bank accounts added yet")
        
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.bank_accounts_notes = st.text_area(
            "Add any notes for Bank Accounts section",
            value=st.session_state.data.bank_accounts_notes,
            key="bank_accounts_notes",
            height=100,
            help="These notes will appear after the Bank Accounts table in the generated certificate"
        )
    
    # Tab 3: Insurance Policies
    with tabs[2]:
        st.header("Life Insurance Policies")
        
        st.subheader("Add New Insurance Policy")
        with st.form("insurance_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                holder_name = st.text_input("Policy Holder Name")
            with col2:
                policy_number = st.text_input("Policy Number")
            with col3:
                amount = st.number_input("Surrender/Maturity Value (INR)", min_value=0.0, step=1000.0, format="%.2f")
            
            if st.form_submit_button("➕ Add Insurance Policy"):
                if holder_name and policy_number:
                    new_policy = InsurancePolicy(
                        holder_name=holder_name,
                        policy_number=policy_number,
                        amount_inr=amount
                    )
                    st.session_state.data.insurance_policies.append(new_policy)
                    st.success("✅ Insurance policy added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.subheader("Current Insurance Policies")
        if st.session_state.data.insurance_policies:
            for idx, policy in enumerate(st.session_state.data.insurance_policies):
                with st.expander(f"Policy {idx+1}: {policy.policy_number}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Holder:** {policy.holder_name}")
                        st.write(f"**Policy No:** {policy.policy_number}")
                    with col2:
                        st.write(f"**Amount (INR):** ₹{policy.amount_inr:,.2f}")
                        st.write(f"**Amount ({st.session_state.data.foreign_currency}):** {policy.amount_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_ins_{idx}"):
                            st.session_state.data.insurance_policies.pop(idx)
                            st.rerun()
            
            st.metric("Total Insurance Value (INR)", f"₹{st.session_state.data.total_insurance_inr:,.2f}")
        else:
            st.info("No insurance policies added yet")
    
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.insurance_policies_notes = st.text_area(
            "Add any notes for Insurance Policies section",
            value=st.session_state.data.insurance_policies_notes,
            key="insurance_policies_notes",
            height=100,
            help="These notes will appear after the Insurance Policies table in the generated certificate"
        )
    
    # Tab 4: P.F. Accounts
    with tabs[3]:
        st.header("Provident Fund (P.F.) Accounts")
        
        st.subheader("Add New P.F. Account")
        with st.form("pf_account_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                holder_name = st.text_input("Account Holder Name")
            with col2:
                pf_number = st.text_input("P.F. Account Number")
            with col3:
                amount = st.number_input("Balance (INR)", min_value=0.0, step=1000.0, format="%.2f")
            
            if st.form_submit_button("➕ Add P.F. Account"):
                if holder_name and pf_number:
                    new_pf = PFAccount(
                        holder_name=holder_name,
                        pf_account_number=pf_number,
                        amount_inr=amount
                    )
                    st.session_state.data.pf_accounts.append(new_pf)
                    st.success("✅ P.F. account added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.subheader("Current P.F. Accounts")
        if st.session_state.data.pf_accounts:
            for idx, acc in enumerate(st.session_state.data.pf_accounts):
                with st.expander(f"P.F. Account {idx+1}: {acc.pf_account_number}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Holder:** {acc.holder_name}")
                    with col2:
                        st.write(f"**Balance (INR):** ₹{acc.amount_inr:,.2f}")
                        st.write(f"**Balance ({st.session_state.data.foreign_currency}):** {acc.amount_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_pf_{idx}"):
                            st.session_state.data.pf_accounts.pop(idx)
                            st.rerun()
            
            st.metric("Total P.F. Balance (INR)", f"₹{st.session_state.data.total_pf_accounts_inr:,.2f}")
        else:
            st.info("No P.F. accounts added yet")
        
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.pf_accounts_notes = st.text_area(
            "Add any notes for P.F. Accounts section",
            value=st.session_state.data.pf_accounts_notes,
            key="pf_accounts_notes",
            height=100,
            help="These notes will appear after the P.F. Accounts table in the generated certificate"
        )
    
    # Tab 5: Deposits
    with tabs[4]:
        st.header("Deposits (FD, RD, etc.)")
        
        st.subheader("Add New Deposit")
        with st.form("deposit_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                holder_name = st.text_input("Investment Holder Name")
            with col2:
                acc_number = st.text_input("A/C Number")
            with col3:
                amount = st.number_input("Amount (INR)", min_value=0.0, step=1000.0, format="%.2f")
            
            if st.form_submit_button("➕ Add Deposit"):
                if holder_name and acc_number:
                    new_deposit = Deposit(
                        holder_name=holder_name,
                        account_number=acc_number,
                        amount_inr=amount
                    )
                    st.session_state.data.deposits.append(new_deposit)
                    st.success("✅ Deposit added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.subheader("Current Deposits")
        if st.session_state.data.deposits:
            for idx, dep in enumerate(st.session_state.data.deposits):
                with st.expander(f"Deposit {idx+1}: {dep.account_number}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Holder:** {dep.holder_name}")
                    with col2:
                        st.write(f"**Amount (INR):** ₹{dep.amount_inr:,.2f}")
                        st.write(f"**Amount ({st.session_state.data.foreign_currency}):** {dep.amount_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_dep_{idx}"):
                            st.session_state.data.deposits.pop(idx)
                            st.rerun()
            
            st.metric("Total Deposit Value (INR)", f"₹{st.session_state.data.total_deposits_inr:,.2f}")
        else:
            st.info("No deposits added yet")
        
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.deposits_notes = st.text_area(
            "Add any notes for Deposits section",
            value=st.session_state.data.deposits_notes,
            key="deposits_notes",
            height=100,
            help="These notes will appear after the Deposits table in the generated certificate"
        )
    
    # Tab 6: NPS
    with tabs[5]:
        st.header("National Pension System (NPS)")
        
        st.subheader("Add New NPS Account")
        with st.form("nps_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                owner_name = st.text_input("Name of Owner")
            with col2:
                pran_number = st.text_input("PRAN No.")
            with col3:
                amount = st.number_input("Amount (INR)", min_value=0.0, step=1000.0, format="%.2f")
            
            if st.form_submit_button("➕ Add NPS Account"):
                if owner_name and pran_number:
                    new_nps = NPSAccount(
                        owner_name=owner_name,
                        pran_number=pran_number,
                        amount_inr=amount
                    )
                    st.session_state.data.nps_accounts.append(new_nps)
                    st.success("✅ NPS account added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.subheader("Current NPS Accounts")
        if st.session_state.data.nps_accounts:
            for idx, nps in enumerate(st.session_state.data.nps_accounts):
                with st.expander(f"NPS Account {idx+1}: {nps.pran_number}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Owner:** {nps.owner_name}")
                    with col2:
                        st.write(f"**Amount (INR):** ₹{nps.amount_inr:,.2f}")
                        st.write(f"**Amount ({st.session_state.data.foreign_currency}):** {nps.amount_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_nps_{idx}"):
                            st.session_state.data.nps_accounts.pop(idx)
                            st.rerun()
            
            st.metric("Total NPS Value (INR)", f"₹{st.session_state.data.total_nps_inr:,.2f}")
        else:
            st.info("No NPS accounts added yet")
        
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.nps_accounts_notes = st.text_area(
            "Add any notes for NPS section",
            value=st.session_state.data.nps_accounts_notes,
            key="nps_accounts_notes",
            height=100,
            help="These notes will appear after the NPS table in the generated certificate"
        )

    # Tab 7: Mutual Funds
    with tabs[6]:
        st.header("Investment in Mutual Funds")

        st.subheader("Add New Mutual Fund")
        with st.form("mf_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                holder_name = st.text_input("Name of the Account Holder")
                folio_number = st.text_input("Policy/Folio Number")
            with col2:
                policy_name = st.text_input("Policy Name")
                amount = st.number_input("Amount (INR)", min_value=0.0, step=1000.0, format="%.2f")

            if st.form_submit_button("➕ Add Mutual Fund"):
                if holder_name and folio_number and policy_name:
                    new_mf = MutualFund(
                        holder_name=holder_name,
                        folio_number=folio_number,
                        policy_name=policy_name,
                        amount_inr=amount
                    )
                    st.session_state.data.mutual_funds.append(new_mf)
                    st.success("✅ Mutual fund added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")

        st.subheader("Current Mutual Funds")
        if st.session_state.data.mutual_funds:
            for idx, mf in enumerate(st.session_state.data.mutual_funds):
                with st.expander(f"Mutual Fund {idx+1}: {mf.policy_name}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Holder:** {mf.holder_name}")
                        st.write(f"**Folio No:** {mf.folio_number}")
                    with col2:
                        st.write(f"**Amount (INR):** ₹{mf.amount_inr:,.2f}")
                        st.write(f"**Amount ({st.session_state.data.foreign_currency}):** {mf.amount_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_mf_{idx}"):
                            st.session_state.data.mutual_funds.pop(idx)
                            st.rerun()
            
            st.metric("Total Mutual Fund Value (INR)", f"₹{st.session_state.data.total_mutual_funds_inr:,.2f}")
        else:
            st.info("No mutual funds added yet")
        
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.mutual_funds_notes = st.text_area(
            "Add any notes for Mutual Funds section",
            value=st.session_state.data.mutual_funds_notes,
            key="mutual_funds_notes",
            height=100,
            help="These notes will appear after the Mutual Funds table in the generated certificate"
        )

    # Tab 8: Shares
    with tabs[7]:
        st.header("Shares & Securities")
        st.subheader("Add New Share Holding")
        with st.form("share_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                company_name = st.text_input("Company Name")
            with col2:
                num_shares = st.number_input("Number of Shares", min_value=1, step=1)
            with col3:
                price = st.number_input("Market Price per Share (INR)", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("➕ Add Share Holding"):
                if company_name and num_shares > 0:
                    new_share = Share(company_name=company_name, num_shares=num_shares, market_price_inr=price)
                    st.session_state.data.shares.append(new_share)
                    st.success("✅ Share holding added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.subheader("Current Share Holdings")
        if st.session_state.data.shares:
            for idx, s in enumerate(st.session_state.data.shares):
                with st.expander(f"Share {idx+1}: {s.company_name}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Company:** {s.company_name}")
                        st.write(f"**Shares:** {s.num_shares}")
                        st.write(f"**Price/Share (INR):** ₹{s.market_price_inr:,.2f}")
                    with col2:
                        st.write(f"**Total Value (INR):** ₹{s.amount_inr:,.2f}")
                        st.write(f"**Total Value ({st.session_state.data.foreign_currency}):** {s.amount_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_share_{idx}"):
                            st.session_state.data.shares.pop(idx)
                            st.rerun()
            
            st.metric("Total Shares Value (INR)", f"₹{st.session_state.data.total_shares_inr:,.2f}")
        else:
            st.info("No shares added yet")
        
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.shares_notes = st.text_area(
            "Add any notes for Shares section",
            value=st.session_state.data.shares_notes,
            key="shares_notes",
            height=100,
            help="These notes will appear after the Shares table in the generated certificate"
        )

    # Tab 9: Vehicles
    with tabs[8]:
        st.header("Vehicles")
        st.subheader("Add New Vehicle")
        with st.form("vehicle_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                vehicle_type = st.selectbox("Vehicle Type", ["Car", "Motorcycle", "Scooter"])
                make_model_year = st.text_input("Make, Model & Year")
            with col2:
                reg_number = st.text_input("Registration Number")
                market_value = st.number_input("Estimated Market Value (INR)", min_value=0.0, format="%.2f")

            if st.form_submit_button("➕ Add Vehicle"):
                if vehicle_type and make_model_year and reg_number:
                    new_vehicle = Vehicle(vehicle_type=vehicle_type, make_model_year=make_model_year, registration_number=reg_number, market_value_inr=market_value)
                    st.session_state.data.vehicles.append(new_vehicle)
                    st.success("✅ Vehicle added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.subheader("Current Vehicles")
        if st.session_state.data.vehicles:
            for idx, v in enumerate(st.session_state.data.vehicles):
                with st.expander(f"Vehicle {idx+1}: {v.vehicle_type} - {v.make_model_year}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Type:** {v.vehicle_type}")
                        st.write(f"**Make/Model/Year:** {v.make_model_year}")
                        st.write(f"**Reg No:** {v.registration_number}")
                    with col2:
                        st.write(f"**Market Value (INR):** ₹{v.market_value_inr:,.2f}")
                        st.write(f"**Market Value ({st.session_state.data.foreign_currency}):** {v.amount_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_vehicle_{idx}"):
                            st.session_state.data.vehicles.pop(idx)
                            st.rerun()
            
            st.metric("Total Vehicle Value (INR)", f"₹{st.session_state.data.total_vehicles_inr:,.2f}")
        else:
            st.info("No vehicles added yet")
        
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.vehicles_notes = st.text_area(
            "Add any notes for Vehicles section",
            value=st.session_state.data.vehicles_notes,
            key="vehicles_notes",
            height=100,
            help="These notes will appear after the Vehicles table in the generated certificate"
        )

    # Tab 10: Post Office Schemes
    with tabs[9]:
        st.header("Post Office Schemes")
        st.subheader("Add New Post Office Scheme")
        with st.form("po_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                scheme_type = st.selectbox("Scheme Type", ["National Savings Certificate (NSC)", "Kisan Vikas Patra (KVP)", "Time Deposit", "Other"])
            with col2:
                acc_number = st.text_input("Certificate/Account Number")
            with col3:
                amount = st.number_input("Investment Amount (INR)", min_value=0.0, format="%.2f")

            if st.form_submit_button("➕ Add Scheme"):
                if scheme_type and acc_number:
                    new_scheme = PostOfficeScheme(scheme_type=scheme_type, account_number=acc_number, amount_inr=amount)
                    st.session_state.data.post_office_schemes.append(new_scheme)
                    st.success("✅ Scheme added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")

        st.subheader("Current Schemes")
        if st.session_state.data.post_office_schemes:
            for idx, p in enumerate(st.session_state.data.post_office_schemes):
                with st.expander(f"Scheme {idx+1}: {p.scheme_type}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Type:** {p.scheme_type}")
                        st.write(f"**Account No:** {p.account_number}")
                    with col2:
                        st.write(f"**Amount (INR):** ₹{p.amount_inr:,.2f}")
                        st.write(f"**Amount ({st.session_state.data.foreign_currency}):** {p.amount_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_po_{idx}"):
                            st.session_state.data.post_office_schemes.pop(idx)
                            st.rerun()
            
            st.metric("Total Post Office Scheme Value (INR)", f"₹{st.session_state.data.total_post_office_inr:,.2f}")
        else:
            st.info("No schemes added yet")
        
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.post_office_schemes_notes = st.text_area(
            "Add any notes for Post Office Schemes section",
            value=st.session_state.data.post_office_schemes_notes,
            key="post_office_schemes_notes",
            height=100,
            help="These notes will appear after the Post Office Schemes table in the generated certificate"
        )

    # Tab 11: Partnership Firms
    with tabs[10]:
        st.header("Investments in Partnership Firms")
        st.subheader("Add New Partnership Firm Investment")
        with st.form("firm_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                firm_name = st.text_input("Name of the Partnership Firm")
                partner_name = st.text_input("Name of the Partner")
                holding_percentage = st.number_input("Percentage of Holdings (%)", min_value=0.0, max_value=100.0, format="%.2f")
            with col2:
                capital_balance = st.number_input("Capital Account Balance (INR)", min_value=0.0, format="%.2f")
                val_date = st.date_input("Valuation Date", value=datetime.date.today())

            if st.form_submit_button("➕ Add Firm Investment"):
                if firm_name and partner_name:
                    new_firm = PartnershipFirm(
                        firm_name=firm_name,
                        partner_name=partner_name,
                        holding_percentage=holding_percentage,
                        capital_balance_inr=capital_balance,
                        valuation_date=val_date.strftime("%d/%m/%Y")
                    )
                    st.session_state.data.partnership_firms.append(new_firm)
                    st.success("✅ Firm investment added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.subheader("Current Firm Investments")
        if st.session_state.data.partnership_firms:
            st.metric("Total Partnership Firm Investment (INR)", f"₹{st.session_state.data.total_partnership_firms_inr:,.2f}")
        else:
            st.info("No firm investments added yet")
        
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.partnership_firms_notes = st.text_area(
            "Add any notes for Partnership Firms section",
            value=st.session_state.data.partnership_firms_notes,
            key="partnership_firms_notes",
            height=100,
            help="These notes will appear after the Partnership Firms table in the generated certificate"
        )

    # Tab 12: Gold/Valuables
    with tabs[11]:
        st.header("Gold & Valuables")
        
        st.subheader("Add Gold Holding")
        with st.form("gold_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                owner_name = st.text_input("Owner Name")
                weight = st.number_input("Weight (grams)", min_value=0.0, step=0.001, format="%.3f")
                rate = st.number_input("Rate per 10g (INR)", min_value=0.0, step=100.0, format="%.2f")
            with col2:
                val_date = st.date_input("Valuation Date", value=datetime.date.today())
                valuer_name = st.text_input("Valuer Name & Details")
            
            if st.form_submit_button("➕ Add Gold Holding"):
                if owner_name and weight > 0:
                    new_gold = GoldHolding(
                        owner_name=owner_name,
                        weight_grams=weight,
                        rate_per_10g=rate,
                        valuation_date=val_date.strftime("%d/%m/%Y"),
                        valuer_name=valuer_name
                    )
                    st.session_state.data.gold_holdings.append(new_gold)
                    st.success("✅ Gold holding added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.subheader("Current Gold Holdings")
        if st.session_state.data.gold_holdings:
            for idx, gold in enumerate(st.session_state.data.gold_holdings):
                with st.expander(f"Gold {idx+1}: {gold.weight_grams}g"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Owner:** {gold.owner_name}")
                        st.write(f"**Weight:** {gold.weight_grams:.3f} grams")
                        st.write(f"**Rate:** ₹{gold.rate_per_10g:,.2f} per 10g")
                    with col2:
                        st.write(f"**Value (INR):** ₹{gold.amount_inr:,.2f}")
                        st.write(f"**Value ({st.session_state.data.foreign_currency}):** {gold.amount_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_gold_{idx}"):
                            st.session_state.data.gold_holdings.pop(idx)
                            st.rerun()
            
            st.metric("Total Gold Value (INR)", f"₹{st.session_state.data.total_gold_inr:,.2f}")
        else:
            st.info("No gold holdings added yet")
    
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.gold_holdings_notes = st.text_area(
            "Add any notes for Gold & Valuables section",
            value=st.session_state.data.gold_holdings_notes,
            key="gold_holdings_notes",
            height=100,
            help="These notes will appear after the Gold & Valuables table in the generated certificate"
        )
    
    # Tab 13: Properties
    with tabs[12]:
        st.header("Immovable Properties")
        
        st.subheader("Add Property")
        with st.form("property_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                owner_name = st.text_input("Owner Name")
                property_type = st.selectbox("Property Type", ["Residential House", "Commercial Property", "Agriculture Land", "Plot"])
                address = st.text_area("Complete Address (with Survey/Khata No.)", height=100)
            with col2:
                valuation = st.number_input("Valuation (INR)", min_value=0.0, step=10000.0, format="%.2f")
                val_date = st.date_input("Valuation Date", value=datetime.date.today())
                valuer_name = st.text_input("Valuer Name & Details")
            
            if st.form_submit_button("➕ Add Property"):
                if owner_name and address:
                    new_property = Property(
                        owner_name=owner_name,
                        property_type=property_type,
                        address=address,
                        valuation_inr=valuation,
                        valuation_date=val_date.strftime("%d/%m/%Y"),
                        valuer_name=valuer_name
                    )
                    st.session_state.data.properties.append(new_property)
                    st.success("✅ Property added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
        
        st.subheader("Current Properties")
        if st.session_state.data.properties:
            for idx, prop in enumerate(st.session_state.data.properties):
                with st.expander(f"Property {idx+1}: {prop.property_type}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Owner:** {prop.owner_name}")
                        st.write(f"**Type:** {prop.property_type}")
                        st.write(f"**Address:** {prop.address}")
                    with col2:
                        st.write(f"**Valuation (INR):** ₹{prop.valuation_inr:,.2f}")
                        st.write(f"**Valuation ({st.session_state.data.foreign_currency}):** {prop.valuation_foreign:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_prop_{idx}"):
                            st.session_state.data.properties.pop(idx)
                            st.rerun()
            
            st.metric("Total Property Value (INR)", f"₹{st.session_state.data.total_immovable_assets_inr:,.2f}")
        else:
            st.info("No properties added yet")
    
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.properties_notes = st.text_area(
            "Add any notes for Properties section",
            value=st.session_state.data.properties_notes,
            key="properties_notes",
            height=100,
            help="These notes will appear after the Properties table in the generated certificate"
        )
    
    # Tab 14: Liabilities
    with tabs[13]:
        st.header("Liabilities")
        
        st.subheader("Add Liability")
        with st.form("liability_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                description = st.text_input("Liability Description (e.g., Home Loan, Personal Loan)")
                amount = st.number_input("Amount (INR)", min_value=0.0, step=10000.0, format="%.2f")
            with col2:
                details = st.text_area("Additional Details", height=100)
            
            if st.form_submit_button("➕ Add Liability"):
                if description:
                    new_liability = Liability(
                        description=description,
                        amount_inr=amount,
                        details=details
                    )
                    st.session_state.data.liabilities.append(new_liability)
                    st.success("✅ Liability added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter liability description")
        
        st.subheader("Current Liabilities")
        if st.session_state.data.liabilities:
            for idx, liab in enumerate(st.session_state.data.liabilities):
                with st.expander(f"Liability {idx+1}: {liab.description}"):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Description:** {liab.description}")
                        st.write(f"**Details:** {liab.details}")
                    with col2:
                        st.write(f"**Amount (INR):** ₹{liab.amount_inr:,.2f}")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_liab_{idx}"):
                            st.session_state.data.liabilities.pop(idx)
                            st.rerun()
            
            st.metric("Total Liabilities (INR)", f"₹{st.session_state.data.total_liabilities_inr:,.2f}")
        else:
            st.info("No liabilities added - Net Worth will equal Total Assets")
    
        st.markdown("---")
        st.subheader("Notes (Optional)")
        st.session_state.data.liabilities_notes = st.text_area(
            "Add any notes for Liabilities section",
            value=st.session_state.data.liabilities_notes,
            key="liabilities_notes",
            height=100,
            help="These notes will appear after the Liabilities table in the generated certificate"
        )
    
    # Tab 15: Summary & Generate
    with tabs[14]:
        st.header("Summary & Generate Certificate")
        
        # Summary Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Movable Assets", f"₹{st.session_state.data.total_movable_assets_inr:,.2f}")
            st.caption(f"Bank: ₹{st.session_state.data.total_bank_balance_inr:,.2f}")
            st.caption(f"Insurance: ₹{st.session_state.data.total_insurance_inr:,.2f}")
            st.caption(f"P.F. Accounts: ₹{st.session_state.data.total_pf_accounts_inr:,.2f}")
            st.caption(f"Deposits: ₹{st.session_state.data.total_deposits_inr:,.2f}")
            st.caption(f"NPS: ₹{st.session_state.data.total_nps_inr:,.2f}")
            st.caption(f"Mutual Funds: ₹{st.session_state.data.total_mutual_funds_inr:,.2f}")
            st.caption(f"Shares: ₹{st.session_state.data.total_shares_inr:,.2f}")
            st.caption(f"Vehicles: ₹{st.session_state.data.total_vehicles_inr:,.2f}")
            st.caption(f"Post Office: ₹{st.session_state.data.total_post_office_inr:,.2f}")
            st.caption(f"Partnership Firms: ₹{st.session_state.data.total_partnership_firms_inr:,.2f}")
            st.caption(f"Gold: ₹{st.session_state.data.total_gold_inr:,.2f}")
        
        with col2:
            st.metric("Total Immovable Assets", f"₹{st.session_state.data.total_immovable_assets_inr:,.2f}")
            st.caption(f"Properties: {len(st.session_state.data.properties)}")
        
        with col3:
            st.metric("Total Liabilities", f"₹{st.session_state.data.total_liabilities_inr:,.2f}")
        
        st.markdown("---")
        
        # Net Worth Display
        st.subheader("💰 NET WORTH CALCULATION")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Net Worth (INR)", 
                f"₹{st.session_state.data.net_worth_inr:,.2f}",
                help="Total Assets - Total Liabilities"
            )
        
        with col2:
            st.metric(
                f"Net Worth ({st.session_state.data.foreign_currency})", 
                f"{st.session_state.data.net_worth_foreign:,.2f}",
                help=f"At exchange rate: {st.session_state.data.exchange_rate} INR = 1 {st.session_state.data.foreign_currency}"
            )
        
        st.markdown("---")
        
        # Validation
        validation_errors = []
        individuals = getattr(st.session_state.data, "individuals", [])
        if not individuals:
            validation_errors.append("❌ At least one individual is required")
        else:
            if any(not ind.full_name.strip() for ind in individuals):
                validation_errors.append("❌ Each individual must have a full name")
            if any(not ind.passport_number.strip() for ind in individuals):
                validation_errors.append(
                    "❌ Each individual must have a passport number"
                )
            if any(not ind.address.strip() for ind in individuals):
                validation_errors.append("❌ Each individual must have an address")
        if not st.session_state.data.embassy_name:
            validation_errors.append("❌ Embassy/Consulate name is required")
        if len(st.session_state.data.bank_accounts) == 0 and len(st.session_state.data.properties) == 0:
            validation_errors.append("⚠️ Add at least one bank account or property")
        if DB_AVAILABLE and not st.session_state.get("selected_person_id"):
            validation_errors.append("❌ Select or create a client from the sidebar before generating")
        
        if validation_errors:
            st.error("Please complete the following:")
            for error in validation_errors:
                st.write(error)
        else:
            st.success("✅ All required information provided. Ready to generate certificate!")
        
        # Generate Button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Show success message if download was completed
            if st.session_state.get('download_completed', False):
                st.success("✅ Report Downloaded Successfully")
                # Clear the flag
                st.session_state.download_completed = False
            
            if st.button("📄 Generate Net Worth Certificate", type="primary", use_container_width=True, disabled=bool(validation_errors)):
                with st.spinner("Generating certificate..."):
                    try:
                        # Generate document
                        doc = generate_networth_certificate(st.session_state.data)
                        
                        # Save to bytes
                        doc_io = io.BytesIO()
                        doc.save(doc_io)
                        doc_io.seek(0)
                        
                        # Store in session state for auto-download
                        primary_name = ""
                        if st.session_state.data.individuals:
                            primary_name = (
                                st.session_state.data.individuals[0]
                                .full_name.replace(" ", "_")
                            )
                        file_name = f"NetWorth_Certificate_{primary_name}_{datetime.date.today().strftime('%Y%m%d')}.docx"
                        certificate_bytes = doc_io.getvalue()

                        if DB_AVAILABLE:
                            try:
                                saved_record = save_certificate(
                                    st.session_state.data,
                                    person_id=st.session_state.get("selected_person_id"),
                                    document_bytes=certificate_bytes,
                                    document_file_name=file_name,
                                    extra_metadata={"source": "streamlit_app"},
                                )
                                st.session_state.last_saved_certificate_id = saved_record.id
                                st.session_state["_show_save_notice"] = True
                                st.session_state.selected_certificate_id = saved_record.id
                            except RepositoryError as repo_err:
                                st.warning(f"Document generated, but saving to the database failed: {repo_err}")
                            except Exception as db_exc:  # pragma: no cover - defensive
                                st.warning(f"Document generated, but storing it failed: {db_exc}")
                        
                        # Encode to base64 for JavaScript download
                        b64_data = base64.b64encode(certificate_bytes).decode()
                        filename_json = json.dumps(file_name)
                        
                        # Show success message immediately
                        st.success("✅ Report Downloaded Successfully")
                        
                        # Trigger download directly via JavaScript
                        # Save scroll position and tab state, then trigger download immediately
                        download_js = f"""
                        <script>
                        (function() {{
                            try {{
                                // Get the main window (not iframe)
                                const mainWindow = window.parent !== window ? window.parent : window;
                                const mainDoc = mainWindow.document;
                                
                                // Save scroll position BEFORE any operations
                                const savedScroll = mainWindow.pageYOffset || mainDoc.documentElement.scrollTop;
                                if (savedScroll > 0) {{
                                    mainWindow.sessionStorage.setItem('preserve_scroll', savedScroll.toString());
                                }}
                                
                                // Save active tab (Summary & Generate is the last tab, index 14)
                                // We want to stay on this tab after rerun
                                mainWindow.sessionStorage.setItem('preserve_tab', '14');
                                
                                // Function to convert base64 to blob
                                function base64ToBlob(base64, mimeType) {{
                                    const byteCharacters = atob(base64);
                                    const byteNumbers = new Array(byteCharacters.length);
                                    for (let i = 0; i < byteCharacters.length; i++) {{
                                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                                    }}
                                    const byteArray = new Uint8Array(byteNumbers);
                                    return new Blob([byteArray], {{ type: mimeType }});
                                }}
                                
                                // Function to trigger download
                                function doDownload() {{
                                    try {{
                                        const data = {json.dumps(b64_data)};
                                        const filename = {filename_json};
                                        const blob = base64ToBlob(data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
                                        const url = mainWindow.URL.createObjectURL(blob);
                                        const a = mainDoc.createElement('a');
                                        a.href = url;
                                        a.download = filename;
                                        a.style.display = 'none';
                                        
                                        // Ensure body exists
                                        if (!mainDoc.body) {{
                                            console.error('Document body not found');
                                            return;
                                        }}
                                        
                                        mainDoc.body.appendChild(a);
                                        a.click();
                                        
                                        // Cleanup after download starts
                                        setTimeout(function() {{
                                            if (mainDoc.body.contains(a)) {{
                                                mainDoc.body.removeChild(a);
                                            }}
                                            mainWindow.URL.revokeObjectURL(url);
                                        }}, 200);
                                        
                                    }} catch (e) {{
                                        console.error('Download error:', e);
                                    }}
                                }}
                                
                                // Function to restore scroll position
                                function restoreScroll() {{
                                    try {{
                                        const saved = mainWindow.sessionStorage.getItem('preserve_scroll');
                                        if (saved && mainWindow.scrollTo) {{
                                            const pos = parseInt(saved);
                                            mainWindow.scrollTo(0, pos);
                                            // Keep trying to restore scroll for a bit (in case of delayed rerender)
                                            let attempts = 0;
                                            const restoreInterval = setInterval(function() {{
                                                attempts++;
                                                const currentScroll = mainWindow.pageYOffset || mainDoc.documentElement.scrollTop;
                                                if (Math.abs(currentScroll - pos) > 10 && attempts < 10) {{
                                                    mainWindow.scrollTo(0, pos);
                                                }} else {{
                                                    clearInterval(restoreInterval);
                                                    mainWindow.sessionStorage.removeItem('preserve_scroll');
                                                }}
                                            }}, 100);
                                        }}
                                    }} catch (e) {{
                                        console.error('Scroll restore error:', e);
                                    }}
                                }}
                                
                                // Execute download immediately if body is ready
                                if (mainDoc.body) {{
                                    doDownload();
                                    // Restore scroll after a short delay
                                    setTimeout(restoreScroll, 50);
                                }} else {{
                                    // Wait for body to be ready
                                    mainWindow.addEventListener('DOMContentLoaded', function() {{
                                        doDownload();
                                        setTimeout(restoreScroll, 50);
                                    }});
                                }}
                                
                                // Function to restore active tab
                                function restoreTab() {{
                                    try {{
                                        const savedTab = mainWindow.sessionStorage.getItem('preserve_tab');
                                        if (savedTab) {{
                                            // Find Streamlit tabs and click the saved one
                                            const tabs = mainDoc.querySelectorAll('[data-baseweb="tab"], [role="tab"]');
                                            const tabIndex = parseInt(savedTab);
                                            if (tabs.length > tabIndex) {{
                                                tabs[tabIndex].click();
                                            }} else {{
                                                // Alternative: find by text content
                                                const tabLabels = mainDoc.querySelectorAll('[data-baseweb="tab"]');
                                                for (let tab of tabLabels) {{
                                                    const text = tab.textContent || tab.innerText || '';
                                                    if (text.includes('Summary') || text.includes('Generate')) {{
                                                        tab.click();
                                                        break;
                                                    }}
                                                }}
                                            }}
                                        }}
                                    }} catch (e) {{
                                        console.error('Tab restore error:', e);
                                    }}
                                }}
                                
                                // Also set up scroll restoration for page reruns
                                setTimeout(restoreScroll, 100);
                                setTimeout(restoreScroll, 300);
                                setTimeout(restoreScroll, 500);
                                
                                // Restore tab after rerun
                                setTimeout(restoreTab, 150);
                                setTimeout(restoreTab, 400);
                                setTimeout(restoreTab, 700);
                                
                            }} catch (e) {{
                                console.error('Script execution error:', e);
                            }}
                        }})();
                        </script>
                        """
                        
                        # Inject JavaScript - this executes immediately in the same render cycle
                        st.components.v1.html(download_js, height=0)
                        
                    except Exception as e:
                        st.error(f"Error generating certificate: {str(e)}")
                        st.exception(e)

        if st.session_state.pop("_show_save_notice", False):
            saved_id = st.session_state.get("last_saved_certificate_id", "")
            st.info(f"Certificate saved to the database. Reference ID: {saved_id}")

if __name__ == "__main__":
    main()
