from __future__ import annotations

from datetime import date, timedelta

from config import MARKETSTACK_API_KEY
from src.data_providers.marketstack import MarketStackAPIClient

PriceMap = dict[date, float]


def load_prices(ticker: str, start_date: date, end_date: date) -> PriceMap:
    client = MarketStackAPIClient(api_key=MARKETSTACK_API_KEY or "")
    response = client.eod_data(
        ticker=ticker,
        date_from=start_date.isoformat(),
        date_to=end_date.isoformat(),
    )

    if not response.get("ok"):
        raise RuntimeError(
            f"Failed to load prices for {ticker}: {response.get('error')}"
        )

    # response["data"] is the raw MarketStack payload: {"data": [...], "pagination": {...}}
    raw = response.get("data", {})
    records = raw.get("data", []) if isinstance(raw, dict) else []

    prices: PriceMap = {}
    for record in records:
        date_str = record.get("date", "")[:10]  # "2024-01-15T00:00:00+0000" -> "2024-01-15"
        close = record.get("close")
        if date_str and close is not None:
            prices[date.fromisoformat(date_str)] = float(close)

    return prices


def nearest_price(prices: PriceMap, target_date: date, max_lookahead: int = 5) -> float | None:
    """
    Returns the closing price on target_date, or the next available trading day
    within max_lookahead days. Handles weekends and market holidays.
    """
    for offset in range(max_lookahead + 1):
        d = target_date + timedelta(days=offset)
        if d in prices:
            return prices[d]
    return None
