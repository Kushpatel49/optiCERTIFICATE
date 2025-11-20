"""
Configuration file for Net Worth Certificate Generator
"""

# CA Partner Details
CA_PARTNERS = {
    "CA HARSH B PATEL": {"membership_no": "600794"},
    "CA PRERIT PAREKH": {"membership_no": "194438"}
}

# Default CA Firm Details
DEFAULT_CA_FIRM_NAME = "Patel Parekh & Associates"
DEFAULT_CA_FRN = "154335W"
DEFAULT_CA_DESIGNATION = "Partner"
DEFAULT_CA_PLACE = "Vijapur"

# Default Exchange Rate
DEFAULT_EXCHANGE_RATE = 63.34

# Supported Currencies
SUPPORTED_CURRENCIES = ["CAD", "USD", "EUR", "GBP", "AUD", "JPY", "CHF", "NZD", "SGD", "HKD"]

# Exchange Rate API
EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/INR"
EXCHANGE_RATE_TIMEOUT = 5

# Document Settings
TABLE_WIDTH_INCHES = 6.5
SR_NO_COLUMN_WIDTH_INCHES = 0.5
DEFAULT_FONT_NAME = "Verdana"
DEFAULT_FONT_SIZE_PT = 11
NET_WORTH_FONT_SIZE_PT = 14

