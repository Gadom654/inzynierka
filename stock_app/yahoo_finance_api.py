# Create a file, e.g., yahoo_finance_api.py

import requests

YAHOO_FINANCE_BASE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"

def get_stock_data(symbol):
    url = f"{YAHOO_FINANCE_BASE_URL}/{symbol}?fields=symbol,shortName,regularMarketPrice,regularMarketOpen,regularMarketDayHigh,regularMarketDayLow"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("quoteSummary", {}).get("result", [])[0]
    else:
        return None
