"""
Exchange rate utility functions
"""

import streamlit as st  
import requests
from config import EXCHANGE_RATE_API_URL, EXCHANGE_RATE_TIMEOUT


def fetch_exchange_rate(currency: str) -> float:
    """
    Fetch real-time exchange rate from INR to the specified currency
    
    Args:
        currency: Currency code (e.g., 'CAD', 'USD')
        
    Returns:
        Exchange rate (INR per 1 unit of foreign currency) or None if failed
    """
    try:
        response = requests.get(EXCHANGE_RATE_API_URL, timeout=EXCHANGE_RATE_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            
            # Get the rate for the selected currency
            if currency in rates:
                # Rate is how many units of foreign currency = 1 INR
                # We need: how many INR = 1 foreign currency
                # So we need to invert: 1 / rate
                rate = 1.0 / rates[currency]
                return round(rate, 2)
            else:
                st.warning(f"Currency {currency} not found in exchange rates. Using default rate.")
                return None
        else:
            st.warning("Unable to fetch exchange rates. Using default rate.")
            return None
    except Exception as e:
        st.warning(f"Error fetching exchange rate: {str(e)}. Using default rate.")
        return None

