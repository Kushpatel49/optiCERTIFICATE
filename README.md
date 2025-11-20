# Net Worth Certificate Generator (ICAI Format)

A robust Streamlit application for generating Net Worth Certificates as per ICAI format for VISA applications.

## 🎯 Features

- ✅ **Complete ICAI Format Compliance** - Follows exact format as per ICAI guidelines
- 📊 **Automatic Calculations** - All totals, subtotals, and currency conversions calculated automatically
- 💱 **Multi-Currency Support** - Supports CAD, USD, EUR, GBP, AUD
- 🔄 **Dynamic Forms** - Add unlimited bank accounts, properties, insurance policies, etc.
- 📱 **User-Friendly Interface** - Clean, intuitive Streamlit UI with tabs
- 📄 **Professional Output** - Generates formatted DOCX documents
- 💾 **Persistent Storage** - Save generated certificates to SQLite (local) or Supabase Postgres (production)
- 👥 **Client History** - Manage clients and reload prior certificates for rapid edits
- ✓ **Validation** - Built-in validation to ensure all required fields are filled

## 📋 What It Generates

The application generates a complete Net Worth Certificate including:

1. **Main Certificate** - Formal certificate with CA signature
2. **Annexure (i)** - Movable Assets Summary
   - Sub-Annexure A: Bank Accounts
   - Sub-Annexure B: Life Insurance Policies
   - Sub-Annexure C: Gold & Valuables
3. **Annexure (ii)** - Immovable Assets (Properties)
4. **Annexure (iii)** - Liabilities
5. **Net Worth Calculation** - Final net worth with notes

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone or download the files**
   ```bash
   # Create a new directory
   mkdir networth-certificate
   cd networth-certificate
   ```

2. **Project files**
   - Ensure the repository structure is preserved (`streamlit_app.py`, `db/`, `alembic/`, etc.)

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

1. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Open in browser**
   - The app will automatically open in your default browser
   - Usually at `http://localhost:8501`

3. **Select or create a client**
   - Use the sidebar to pick an existing client or add a new one
   - Loading a client auto-populates their last saved certificate

4. **Fill in the information**
   - Navigate through tabs to enter all required information
   - All calculations happen automatically

5. **Generate certificate**
   - Review summary in the final tab
   - Click "Generate Net Worth Certificate"
   - Download the generated DOCX file

## 🗄️ Database Persistence

The application now stores generated certificates for later retrieval via the sidebar history.

### Local Development (SQLite)

- By default, the app creates `networth.db` at the project root.
- Tables are auto-created on first run via SQLAlchemy `create_all()`.
- No additional configuration is required for local testing.

### Production (Supabase Postgres)

1. Provision a Supabase project and note the *database connection string*.
2. Create `.streamlit/secrets.toml` with:
   ```toml
   [database]
   url = "postgresql+psycopg2://<user>:<password>@<host>:5432/<db>"
   ```
3. Run migrations:
   ```bash
   alembic upgrade head
   ```
4. Deploy / run Streamlit with the same `DATABASE_URL` (environment variable or secrets).

### Alembic Management

- Generate new migrations: `alembic revision --autogenerate -m "describe change"`
- Apply migrations: `alembic upgrade head`
- Downgrade: `alembic downgrade -1`

## 👥 Client Management Workflow

- Use the sidebar to **select an existing client** or **create a new client** before generating a certificate.
- Loading a certificate from the sidebar repopulates every tab, allowing quick edits and regenerated reports without retyping.
- Each generated certificate is versioned; the most recent entry is shown at the top of the client’s history.
- The app enforces client selection when the database layer is active to ensure every certificate is associated with the correct person.

## 📝 Input Fields Guide

### Tab 1: Basic Info
- **Personal Details**
  - Individual's Full Name (Required)
  - Individual's Address (Required)
  - Certificate Date
  - Engagement Letter Date

- **Embassy Details**
  - Embassy/Consulate Name (Required)
  - Embassy Address (Required)

- **Currency Settings**
  - Foreign Currency (CAD/USD/EUR/GBP/AUD)
  - Exchange Rate (INR to Foreign Currency)

### Tab 2: Bank Accounts
For each bank account:
- Account Holder Name
- Account Number
- Bank Name
- Balance (INR)
- Statement Date

### Tab 3: Insurance Policies
For each policy:
- Policy Holder Name
- Policy Number
- Surrender/Maturity Value (INR)

### Tab 4: Gold & Valuables
For each gold holding:
- Owner Name
- Weight (grams)
- Rate per 10g (INR)
- Valuation Date
- Valuer Name & Details

### Tab 5: Properties
For each property:
- Owner Name
- Property Type (Residential/Commercial/Agricultural/Plot)
- Complete Address (with Survey/Khata numbers)
- Valuation (INR)
- Valuation Date
- Valuer Name & Details

### Tab 6: Liabilities
For each liability:
- Description (e.g., Home Loan)
- Amount (INR)
- Additional Details

### Tab 7: Summary & Generate
- Review all entered data
- See calculated net worth
- Generate and download certificate

## 🔧 Pre-configured CA Details

The following CA details are pre-configured (can be modified in code):

- **Firm Name:** Patel Parekh & Associates
- **FRN:** 154335W
- **Partner Name:** CA Harsh B Patel
- **Membership No:** 600794
- **Designation:** Partner
- **Place:** Vijapur

To change these, modify the `NetWorthData` class defaults in the code.

## 💡 Key Features Explained

### Automatic Calculations
- **Bank totals** - Automatically sums all bank account balances
- **Insurance totals** - Sums all policy values
- **Gold totals** - Calculates gold value from weight × rate
- **Property totals** - Sums all property valuations
- **Net Worth** - Automatically calculates: (Total Assets - Total Liabilities)
- **Currency Conversion** - All amounts auto-converted to foreign currency

### Data Validation
- Ensures required fields are filled
- Validates numerical inputs
- Prevents certificate generation with incomplete data

### Document Structure
- Maintains exact ICAI format
- Professional formatting with tables
- Proper page breaks and sections
- Bold/underline formatting as per original

## 📊 Example Calculation Flow

```
Movable Assets:
  ├─ Bank Accounts: ₹11,64,108.15
  ├─ Insurance: ₹2,53,618.00
  └─ Gold: ₹43,75,292.00
  Total: ₹57,93,018.15

Immovable Assets:
  └─ Properties: ₹3,98,57,000.00

Total Assets: ₹4,56,50,018.15

Liabilities: ₹0.00

Net Worth = ₹4,56,50,018.15
```

## 🛠️ Customization

### Change CA Details
Edit the `NetWorthData` class defaults:
```python
ca_firm_name: str = "Your Firm Name"
ca_frn: str = "Your FRN"
ca_partner_name: str = "Your Name"
ca_membership_no: str = "Your Number"
```

### Add More Currency Options
Edit the currency selectbox:
```python
st.selectbox("Foreign Currency", 
    ["CAD", "USD", "EUR", "GBP", "AUD", "JPY", "CHF"])
```

### Modify Document Styling
Edit the `generate_networth_certificate()` function to change fonts, sizes, or formatting.

## 🐛 Troubleshooting

### Issue: Module not found
**Solution:** Run `pip install -r requirements.txt`

### Issue: Port already in use
**Solution:** Use a different port:
```bash
streamlit run app.py --server.port 8502
```

### Issue: Document not downloading
**Solution:** Check browser popup blocker settings

### Issue: Calculations incorrect
**Solution:** Verify exchange rate and all input amounts

## 📸 Screenshot Guide

**Main Interface:** Clean tabbed interface for easy navigation

**Bank Accounts Tab:** Add multiple bank accounts with automatic totaling

**Summary Tab:** Complete overview with net worth calculation

## ⚠️ Important Notes

1. **UDIN Field:** The UDIN (Unique Document Identification Number) field is left blank in the generated document. The CA should generate and fill this separately after signing.

2. **Valuation Certificates:** Ensure you have proper valuation certificates for gold and properties before generating the final certificate.

3. **Document Verification:** Always review the generated document before submission to ensure accuracy.

4. **Currency Rates:** Update exchange rates regularly for accurate conversions.

5. **Data Storage:** Certificates are persisted when a database is configured (SQLite/Supabase). If the database layer is unavailable, data remains session-scoped.

## 📄 Output Format

The generated document is a Microsoft Word (.docx) file that includes:
- Professional formatting
- Proper tables with borders
- Bold/underline as per ICAI format
- Multiple annexures
- Signature blocks
- All calculations pre-filled

## 🔐 Data Privacy

- All data processing happens locally unless you configure Supabase Postgres.
- When a remote database URL is supplied, certificate snapshots and DOCX binaries are stored in that database.
- Generated documents are downloaded directly to your system; you can remove stored records via your database console if required.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure Python version is 3.8+

## 📜 License

This tool is provided as-is for generating Net Worth Certificates as per ICAI format. Users are responsible for ensuring the accuracy of data entered and compliance with local regulations.

## 🎓 Credits

- Format based on ICAI guidelines for Net Worth Certificates
- Built with Streamlit and python-docx
- Designed for CA firms and professionals

---

**Version:** 1.0.0  
**Last Updated:** October 2025  
**Compatible with:** ICAI Net Worth Certificate Format for VISA Applications