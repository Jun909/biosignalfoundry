from os import getenv

from dotenv import load_dotenv
from fredapi import Fred

from src.data_providers import AlphaVintageAPIClient
# from src.data_providers.finnhub import FinnHubAPIClient
# from src.data_providers.fred import FredAPIClient
# from src.data_providers.marketstack import MarketStackAPIClient
# from src.data_providers.massive import MassiveAPIClient
# from src.data_providers.openfda import (Dataset, OpenFDAAPIClient, Query,
#                                         SearchClause)
# from data_providers import AlphaVintageAPIClient
load_dotenv()

alphavintagekey = getenv("ALPHAVANTAGE_API_KEY")
avclient = AlphaVintageAPIClient(api_key=alphavintagekey or "")

REDUNDANT_FIELDS = {"costofGoodsAndServicesSold"}

NUMERIC_FIELDS = {
    "grossProfit", "totalRevenue", "costOfRevenue", "operatingIncome",
    "sellingGeneralAndAdministrative", "researchAndDevelopment", "operatingExpenses",
    "netInterestIncome", "interestIncome", "interestExpense", "depreciationAndAmortization",
    "incomeBeforeTax", "incomeTaxExpense", "netIncomeFromContinuingOperations",
    "ebit", "ebitda", "netIncome", "otherNonOperatingIncome"
}

def _process_income_statement(raw_response: dict, years: int) -> dict:
    if not raw_response.get("ok"):
        raise ValueError("Income statement response indicates failure.")

    records: list[dict] = raw_response["data"][0]
    ticker: str = raw_response["ticker"]
    truncated = records[:years]

    keys_to_drop = {
        key for key in truncated[0].keys()
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

def get_income_statement_annual(ticker: str, years: int = 5) -> dict:
    raw = avclient.get_income_statement_annual(ticker=ticker)
    return _process_income_statement(raw, years=years)

print(get_income_statement_annual(ticker="LLY"))