from langchain.tools import tool

from config import ALPHAVANTAGE_API_KEY, FINNHUB_API_KEY
from src.data_providers import AlphaVintageAPIClient
from src.data_providers.finnhub import FinnHubAPIClient

# from src.data_providers.fred import FredAPIClient
# from src.data_providers.marketstack import MarketStackAPIClient
# from src.data_providers.massive import MassiveAPIClient
# from src.data_providers.openfda import (Dataset, OpenFDAAPIClient, Query,
#                                         SearchClause)
# from data_providers import AlphaVintageAPIClient

avclient = AlphaVintageAPIClient(api_key=ALPHAVANTAGE_API_KEY or "")
finnclient = FinnHubAPIClient(api_key=FINNHUB_API_KEY or "")

REDUNDANT_FIELDS = {"costofGoodsAndServicesSold"}

NUMERIC_FIELDS = {
    "grossProfit",
    "totalRevenue",
    "costOfRevenue",
    "operatingIncome",
    "sellingGeneralAndAdministrative",
    "researchAndDevelopment",
    "operatingExpenses",
    "netInterestIncome",
    "interestIncome",
    "interestExpense",
    "depreciationAndAmortization",
    "incomeBeforeTax",
    "incomeTaxExpense",
    "netIncomeFromContinuingOperations",
    "ebit",
    "ebitda",
    "netIncome",
    "otherNonOperatingIncome",
}

COMPANY_PROFILE_FIELDS_TO_KEEP = {
    "name",
    "country",
    "currency",
    "exchange",
    "finnhubIndustry",
    "ipo",
    "marketCapitalization",
    "shareOutstanding",
    "weburl",
}


def _process_income_statement(raw_response: dict, years: int) -> dict:
    """
    Optimize the raw output from AlphaVantage API wrapper. Only shows income statement of last 5 years by default instead of 20 years.
    Truncate outputs by removing keys that has 'None' as values.
    """
    if not raw_response.get("ok"):
        ticker = raw_response.get("ticker", "unknown")
        error = raw_response.get("error", "Unknown error")
        raise ValueError(f"[{ticker}] Income statement fetch failed: {error}")

    records: list[dict] = raw_response["data"][0]
    ticker: str = raw_response["ticker"]
    truncated = records[:years]

    keys_to_drop = {
        key
        for key in truncated[0].keys()
        if all(record.get(key) in (None, "None") for record in truncated)
    } | REDUNDANT_FIELDS

    cleaned_records = []
    for record in truncated:
        cleaned = {}
        for key, value in record.items():
            if key in keys_to_drop or value in (None, "None"):
                continue
            try:
                num = float(value)
                cleaned[key] = round(num / 1e9, 3) if key in NUMERIC_FIELDS else num
            except (ValueError, TypeError):
                cleaned[key] = value
        cleaned_records.append(cleaned)

    return {
        "ticker": ticker,
        "currency_unit": "USD_billions",
        "fiscal_years": [r["fiscalDateEnding"] for r in cleaned_records],
        "statements": cleaned_records,
    }


def _process_company_profile(raw_response: dict) -> dict:
    if not raw_response.get("ok"):
        ticker = raw_response.get("ticker", "unknown")
        error = raw_response.get("error", "Unknown error")
        raise ValueError(f"[{ticker}] Company profile fetch failed: {error}")

    data = raw_response["data"]

    return {
        "ticker": raw_response["ticker"],
        "profile": {
            k: v for k, v in data.items() if k in COMPANY_PROFILE_FIELDS_TO_KEEP
        },
    }


@tool
def get_income_statement_annual(ticker: str, years: int = 5) -> dict:
    """
    Provides the annual income statement of a company.
    Args:
        ticker: The ticker of a company. Example: AAPL for Apple, MSFT for Microsoft
        years: Length of past years to track. Default is last 5 years.
    """
    raw = avclient.get_income_statement_annual(ticker=ticker)
    return _process_income_statement(raw, years=years)


@tool
def get_company_profile(ticker: str) -> dict:
    """
    Provides basic company profile information.
    Args:
        ticker: The ticker of a company. Example: AAPL for Apple, MSFT for Microsoft
    """
    raw = finnclient.company_profile2(ticker=ticker)
    return _process_company_profile(raw)



