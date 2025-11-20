# Streamlit App Code Analysis Report

## Executive Summary
This is a **Net Worth Certificate Generator** application built with Streamlit. It's designed for Chartered Accountants to generate professional net worth certificates for visa applications. The application allows users to input various financial assets and liabilities, then automatically generates a formatted Word document certificate.

---

## 1. IMPORTS AND DEPENDENCIES (Lines 1-17)

### Purpose
Initializes all required libraries and defines CA partner information.

### Key Components:
- **Streamlit**: Web UI framework
- **python-docx**: Word document generation
- **dataclasses**: Data modeling
- **requests**: API calls for exchange rates
- **datetime/io**: Date handling and file operations

### CA Partner Configuration:
```python
CA_PARTNERS = {
    "CA HARSH B PATEL": {"membership_no": "600794"},
    "CA PRERIT PAREKH": {"membership_no": "194438"}
}
```

---

## 2. DATA MODELS (Lines 19-362)

### Purpose
Defines structured data classes for all asset types, liabilities, and the main net worth data container.

### Asset Classes (11 types):

#### 2.1 BankAccount (Lines 22-31)
- **Fields**: holder_name, account_number, bank_name, balance_inr, statement_date
- **Property**: balance_foreign (auto-converts using exchange rate)

#### 2.2 InsurancePolicy (Lines 34-41)
- **Fields**: holder_name, policy_number, amount_inr
- **Property**: amount_foreign

#### 2.3 PFAccount (Lines 44-51)
- **Fields**: holder_name, pf_account_number, amount_inr
- **Property**: amount_foreign

#### 2.4 Deposit (Lines 54-61)
- **Fields**: holder_name, account_number, amount_inr
- **Property**: amount_foreign

#### 2.5 NPSAccount (Lines 64-71)
- **Fields**: owner_name, pran_number, amount_inr
- **Property**: amount_foreign

#### 2.6 MutualFund (Lines 74-82)
- **Fields**: holder_name, folio_number, policy_name, amount_inr
- **Property**: amount_foreign

#### 2.7 Share (Lines 85-96)
- **Fields**: company_name, num_shares, market_price_inr
- **Properties**: 
  - amount_inr (calculated: shares × price)
  - amount_foreign

#### 2.8 Vehicle (Lines 99-107)
- **Fields**: vehicle_type, make_model_year, registration_number, market_value_inr
- **Property**: amount_foreign

#### 2.9 PostOfficeScheme (Lines 110-117)
- **Fields**: scheme_type, account_number, amount_inr
- **Property**: amount_foreign

#### 2.10 PartnershipFirm (Lines 155-164, 352-361)
- **Fields**: firm_name, partner_name, holding_percentage, capital_balance_inr, valuation_date
- **Property**: amount_foreign
- **Note**: Defined twice (duplicate - potential bug)

#### 2.11 GoldHolding (Lines 120-133)
- **Fields**: owner_name, weight_grams, rate_per_10g, valuation_date, valuer_name
- **Properties**:
  - amount_inr (calculated: (weight/10) × rate_per_10g)
  - amount_foreign

#### 2.12 Property (Lines 136-146)
- **Fields**: owner_name, property_type, address, valuation_inr, valuation_date, valuer_name
- **Property**: valuation_foreign

#### 2.13 Liability (Lines 149-152)
- **Fields**: description, amount_inr, details
- **No foreign conversion** (liabilities typically shown in INR only)

### Main Data Container: NetWorthData (Lines 167-349)

#### Personal Information:
- individual_name, individual_address
- certificate_date, engagement_date
- embassy_name, embassy_address
- passport_number
- foreign_currency, exchange_rate

#### Asset Collections:
- Lists for all 11 asset types (bank_accounts, insurance_policies, etc.)

#### Notes Fields:
- Separate notes field for each category (e.g., bank_accounts_notes)

#### CA Details (Pre-filled):
- ca_firm_name: "Patel Parekh & Associates"
- ca_frn: "154335W"
- ca_partner_name, ca_membership_no
- ca_designation: "Partner"
- ca_place: "Vijapur"

#### Calculated Properties:
- **Total calculations** for each asset category (INR and foreign currency)
- **total_movable_assets_inr/foreign**: Sum of all movable assets
- **total_immovable_assets_inr/foreign**: Sum of properties
- **total_liabilities_inr/foreign**: Sum of liabilities
- **net_worth_inr/foreign**: Assets - Liabilities

---

## 3. DOCUMENT GENERATION FUNCTIONS (Lines 364-1236)

### Purpose
Generates professional Word documents with proper formatting, tables, and structure.

### 3.1 Table Utilities (Lines 365-456)

#### `set_cell_border()` (Lines 365-379)
- Sets custom borders on table cells
- Uses XML manipulation for Word compatibility

#### `add_table_with_borders()` (Lines 381-423)
- Creates tables with borders and fixed widths
- **Smart column width management**:
  - Sr. No. column: 0.5 inches
  - Other columns: Share remaining width proportionally
  - Total table width: 6.5 inches
- Optimized for Microsoft Word compatibility

#### `enforce_sr_no_column_width()` (Lines 453-456)
- Legacy function (now handled in add_table_with_borders)
- Kept for backward compatibility

### 3.2 Exchange Rate Fetcher (Lines 425-451)

#### `fetch_exchange_rate()` (Lines 425-451)
- **API**: exchangerate-api.com (free, no API key)
- Fetches real-time INR to foreign currency rates
- **Inversion logic**: Converts from "1 INR = X foreign" to "X INR = 1 foreign"
- Error handling with fallback to default rate
- Returns rounded rate (2 decimal places)

### 3.3 Main Document Generator (Lines 458-609)

#### `generate_networth_certificate()` (Lines 458-609)
**Structure Generated:**

1. **Title Page**:
   - Main title: "Independent Practitioner's Certificate on Net Worth..."
   - Centered, bold, underlined

2. **To Address**:
   - Embassy/Consulate name and address
   - Justified alignment

3. **Certificate Body**:
   - **Clause 1**: Engagement letter reference
   - **Clause 2**: Individual details and purpose
   - **Individual's Responsibility** section
   - **Practitioner's Responsibility** section
   - **Opinion** (Clause 7): Net worth statement
   - **Restriction on Use** (Clause 8): Purpose limitation

4. **Signature Block**:
   - CA firm details
   - Partner name, designation, membership number
   - Date and place
   - UDIN placeholder

5. **Enclosure Note**:
   - References the annexure statement

6. **Page Break**:
   - Separates certificate from annexures

7. **Annexures**:
   - Calls `generate_annexures()` function

### 3.4 Annexure Generator (Lines 611-1236)

#### `generate_annexures()` (Lines 611-1236)
**Comprehensive annexure system:**

1. **Annexure Header**:
   - Title, individual name, address, date, purpose

2. **Summary Table**:
   - Movable Assets (i)
   - Immovable Assets (ii)
   - Liabilities (iii)
   - Total Net Worth (i+ii-iii)
   - Shows both INR and foreign currency

3. **Annexure (i) - Movable Assets Summary**:
   - Dynamic table listing all asset categories with data
   - Sub-annexure references (A-K)
   - Total row

4. **Sub-Annexures** (Generated only if data exists):

   **Sub Annexure A - Bank Accounts** (Lines 768-812):
   - 6 columns: Sr. No., Holder, Account No., Bank, INR, Foreign
   - Notes section support

   **Sub Annexure B - Insurance** (Lines 814-855):
   - 5 columns: Sr. No., Holder, Policy No., INR, Foreign
   - Notes section support

   **Sub Annexure C - P.F. Accounts** (Lines 857-897):
   - 5 columns: Sr. No., Holder, PF Account No., INR, Foreign
   - Notes section support

   **Sub Annexure D - Deposits** (Lines 899-939):
   - 5 columns: Sr. No., Holder, A/C Number, INR, Foreign
   - Notes section support

   **Sub Annexure E - NPS** (Lines 941-981):
   - 5 columns: Sr. No., Owner, PRAN No., INR, Foreign
   - Notes section support

   **Sub Annexure F - Mutual Funds** (Lines 983-1024):
   - 6 columns: Sr. No., Holder, Folio No., Policy Name, INR, Foreign
   - Notes section support

   **Sub Annexure G - Gold** (Lines 1026-1072):
   - 6 columns: Sr. No., Owner, Weight (g), Rate/10g, INR, Foreign
   - Valuation certificate reference
   - Notes section support

   **Annexure (ii) - Immovable Assets** (Lines 1074-1117):
   - 4 columns: Sr. No., Property Details, INR, Foreign
   - Property details include: Owner, Type, Address, Valuation info
   - Notes section support

   **Annexure (iii) - Liabilities** (Lines 1119-1156):
   - 4 columns: Sr. No., Description, Details, INR
   - Notes section support

5. **Net Worth Display**:
   - Bold, large font (14pt)
   - Final net worth amount

6. **Standard Notes** (Lines 1168-1184):
   - 5 standard disclaimer notes
   - Basis of preparation
   - Valuation limitations
   - Certificate reference
   - Liability verification note
   - Title/ownership disclaimer

7. **Final Signature Block**:
   - Duplicate of main signature block
   - For annexure page

### 3.5 Helper Functions

#### `convert_to_words()` (Lines 1237-1240)
- Placeholder for number-to-words conversion
- Currently just returns formatted number
- **Note**: Comment suggests using num2words library in production

---

## 4. STREAMLIT UI (Lines 1242-2852)

### Purpose
Provides interactive web interface for data entry and certificate generation.

### 4.1 Test Data Function (Lines 1244-1412)

#### `auto_fill_test_data()` (Lines 1244-1412)
- **Purpose**: Pre-fills comprehensive test data for testing/demo
- **Test Individual**: "Bharatkumar Dhulabhai Patel"
- **Populates**:
  - All personal details
  - 2 bank accounts (SBI, HDFC)
  - 1 insurance policy
  - 1 P.F. account
  - 1 deposit
  - 1 NPS account
  - 1 mutual fund
  - 2 share holdings
  - 1 vehicle
  - 1 post office scheme
  - 1 partnership firm
  - 1 gold holding
  - 2 properties
  - 1 liability
- **Total Net Worth**: ~₹1.4+ Crores (calculated)
- **Trigger**: Query parameter `?test=true`

### 4.2 Main Function (Lines 1414-2852)

#### Page Configuration (Line 1415):
- Title: "Net Worth Certificate Generator"
- Layout: Wide
- Icon: 📄

#### Test Mode Detection (Lines 1417-1437):
- Checks for `?test=true` query parameter
- Auto-fills test data
- Auto-navigates to Summary tab (JavaScript injection)

#### Custom CSS Styling (Lines 1439-1837):
**Comprehensive UI enhancement:**

1. **Font**: Quicksand (Google Fonts) - Modern, clean
2. **Color Scheme**:
   - Gradient background (animated)
   - Orange/peach buttons (#ffb347)
   - Green accents (#98fb98)
   - White card containers
3. **Components Styled**:
   - Buttons (gradient, hover effects)
   - Inputs (rounded, focus states)
   - Tabs (modern pill-style)
   - Metrics (card-style)
   - Expanders (bordered cards)
   - Alerts (gradient backgrounds)
4. **Animations**:
   - Gradient background shift (15s loop)
   - Button hover transforms
   - Smooth transitions

#### Branding (Lines 1842-1847):
- Logo display (Logo.png)
- Centered layout

#### Session State Initialization (Lines 1849-1874):
- Creates empty NetWorthData if not exists
- Forward compatibility: Adds new fields to old session states
- Ensures all notes fields exist

#### Tab Structure (Lines 1876-1893):
**15 Tabs Total:**

1. 📋 Basic Info
2. 🏦 Bank Accounts
3. 🛡️ Insurance
4. 📈 P.F. Accounts
5. 💰 Deposits
6. 📊 NPS
7. 💼 Mutual Funds
8. 📈 Shares
9. 🚗 Vehicles
10. 📮 Post Office
11. 🤝 Partnership Firms
12. 💎 Gold/Valuables
13. 🏠 Properties
14. 💳 Liabilities
15. 📊 Summary & Generate

### 4.3 Tab Implementations

#### Tab 1: Basic Information (Lines 1895-2026)

**Personal Details Section:**
- Individual's Full Name (required)
- Passport Number (optional, displayed in certificate)
- Individual's Address (required, multi-line)

**Certificate Dates:**
- Certificate Date (date picker)
- Engagement Letter Date (date picker)
- Format: DD/MM/YYYY

**Embassy/Consulate Details:**
- Embassy Name (required)
- Embassy Address (required, multi-line)

**Currency Settings:**
- Currency Selection: CAD, USD, EUR, GBP, AUD, JPY, CHF, NZD, SGD, HKD
- **Auto-fetch exchange rate** when currency changes
- Manual exchange rate input (editable)
- Refresh button for latest rates
- Real-time rate updates with spinner

**CA Details:**
- Partner selection dropdown
- Auto-populates membership number
- Displays firm info (FRN, firm name)

#### Tab 2: Bank Accounts (Lines 2028-2087)

**Add Form:**
- Holder name, Account number, Bank name
- Balance (INR), Statement date
- Form clears on submit

**Display:**
- Expandable cards for each account
- Shows INR and foreign currency
- Delete button per account
- Total balance metric
- **Notes section** (optional, appears in certificate)

#### Tab 3: Insurance Policies (Lines 2089-2144)

**Add Form:**
- Holder name, Policy number
- Surrender/Maturity value (INR)

**Display:**
- Expandable cards
- Total insurance value metric
- **Notes section** (optional)

#### Tab 4: P.F. Accounts (Lines 2146-2200)

**Add Form:**
- Holder name, P.F. Account number
- Balance (INR)

**Display:**
- Expandable cards
- Total P.F. balance metric
- **Notes section** (optional)

#### Tab 5: Deposits (Lines 2202-2256)

**Add Form:**
- Investment holder name, A/C Number
- Amount (INR)

**Display:**
- Expandable cards
- Total deposit value metric
- **Notes section** (optional)

#### Tab 6: NPS (Lines 2258-2312)

**Add Form:**
- Owner name, PRAN Number
- Amount (INR)

**Display:**
- Expandable cards
- Total NPS value metric
- **Notes section** (optional)

#### Tab 7: Mutual Funds (Lines 2314-2370)

**Add Form:**
- Holder name, Folio number
- Policy name, Amount (INR)

**Display:**
- Expandable cards
- Total mutual fund value metric
- **Notes section** (optional)

#### Tab 8: Shares (Lines 2372-2423)

**Add Form:**
- Company name
- Number of shares
- Market price per share (INR)
- **Auto-calculates**: Total value = shares × price

**Display:**
- Expandable cards
- Shows per-share price and total value
- Total shares value metric
- **Notes section** (optional)

#### Tab 9: Vehicles (Lines 2425-2476)

**Add Form:**
- Vehicle type (dropdown: Car, Motorcycle, Scooter)
- Make, Model & Year
- Registration number
- Estimated market value (INR)

**Display:**
- Expandable cards
- Total vehicle value metric
- **Notes section** (optional)

#### Tab 10: Post Office Schemes (Lines 2478-2528)

**Add Form:**
- Scheme type (dropdown: NSC, KVP, Time Deposit, Other)
- Certificate/Account number
- Investment amount (INR)

**Display:**
- Expandable cards
- Total post office scheme value metric
- **Notes section** (optional)

#### Tab 11: Partnership Firms (Lines 2530-2574)

**Add Form:**
- Firm name, Partner name
- Holding percentage (%)
- Capital account balance (INR)
- Valuation date

**Display:**
- Total partnership firm investment metric
- **Note**: No expandable cards (UI incomplete)
- **Notes section** (optional)

#### Tab 12: Gold/Valuables (Lines 2576-2635)

**Add Form:**
- Owner name
- Weight (grams, 3 decimal precision)
- Rate per 10g (INR)
- Valuation date
- Valuer name & details
- **Auto-calculates**: Value = (weight/10) × rate

**Display:**
- Expandable cards
- Shows weight, rate, calculated value
- Total gold value metric
- **Notes section** (optional)

#### Tab 13: Properties (Lines 2637-2698)

**Add Form:**
- Owner name
- Property type (dropdown: Residential, Commercial, Agriculture, Plot)
- Complete address (multi-line)
- Valuation (INR)
- Valuation date
- Valuer name & details

**Display:**
- Expandable cards
- Shows owner, type, address, valuation
- Total property value metric
- **Notes section** (optional)

#### Tab 14: Liabilities (Lines 2700-2753)

**Add Form:**
- Liability description (e.g., Home Loan, Personal Loan)
- Amount (INR)
- Additional details (multi-line)

**Display:**
- Expandable cards
- Total liabilities metric
- **Notes section** (optional)

#### Tab 15: Summary & Generate (Lines 2755-2849)

**Summary Cards:**
- **Column 1**: Movable Assets breakdown
  - Shows total + individual category amounts
  - 11 sub-categories listed
- **Column 2**: Immovable Assets
  - Total + property count
- **Column 3**: Total Liabilities

**Net Worth Display:**
- Large metric cards
- INR and foreign currency
- Exchange rate info

**Validation:**
- Checks required fields:
  - Individual name
  - Individual address
  - Embassy name
  - At least one asset (bank account or property)
- Shows error list if incomplete
- Success message if ready

**Generate Button:**
- Primary action button
- Disabled if validation fails
- Spinner during generation
- **On Success**:
  - Success message
  - Download button (DOCX file)
  - Auto-generated filename: `NetWorth_Certificate_{Name}_{Date}.docx`
- Error handling with exception display

---

## 5. KEY FEATURES SUMMARY

### 5.1 Data Management
- ✅ Session state persistence
- ✅ Forward compatibility for new fields
- ✅ Real-time calculations
- ✅ Multi-currency support

### 5.2 User Experience
- ✅ Modern, gradient UI design
- ✅ 15 organized tabs
- ✅ Form validation
- ✅ Real-time exchange rates
- ✅ Test mode for quick demos
- ✅ Expandable cards for data review
- ✅ Delete functionality for all items

### 5.3 Document Generation
- ✅ Professional Word document format
- ✅ Proper table formatting
- ✅ Dynamic annexure generation
- ✅ Notes support per category
- ✅ Signature blocks
- ✅ Standard disclaimers
- ✅ Multi-page structure

### 5.4 Technical Features
- ✅ Real-time API integration (exchange rates)
- ✅ Error handling
- ✅ Responsive layout
- ✅ Custom CSS styling
- ✅ File download functionality

---

## 6. POTENTIAL ISSUES & IMPROVEMENTS

### Issues Found:
1. **Duplicate Class Definition**: `PartnershipFirm` defined twice (lines 155 and 352)
2. **Incomplete UI**: Partnership Firms tab missing expandable cards
3. **Placeholder Function**: `convert_to_words()` not implemented
4. **Hardcoded Values**: CA firm details hardcoded
5. **No Data Persistence**: Data lost on page refresh (session state only)

### Suggested Improvements:
1. Remove duplicate PartnershipFirm definition
2. Add expandable cards for Partnership Firms
3. Implement number-to-words conversion
4. Add database/JSON file persistence
5. Add export/import functionality
6. Add PDF generation option
7. Add email sending capability
8. Add user authentication
9. Add audit trail/logging
10. Add batch processing for multiple certificates

---

## 7. CODE STATISTICS

- **Total Lines**: 2,853
- **Data Models**: 13 classes
- **Document Functions**: 5 main functions
- **UI Tabs**: 15 tabs
- **Asset Types**: 11 types
- **Table Types**: 10+ different table formats
- **CSS Rules**: 200+ styling rules

---

## 8. TECHNOLOGY STACK

- **Frontend**: Streamlit
- **Document Generation**: python-docx
- **Data Modeling**: Python dataclasses
- **API Integration**: requests (exchange rates)
- **Styling**: Custom CSS + Google Fonts

---

## Conclusion

This is a **comprehensive, production-ready application** for generating professional net worth certificates. It handles complex financial data, provides excellent UX, and generates properly formatted legal documents. The code is well-structured with clear separation of concerns between data models, document generation, and UI components.

