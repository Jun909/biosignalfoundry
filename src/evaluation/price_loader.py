from __future__ import annotations

from datetime import date, timedelta

import yfinance as yf

PriceMap = dict[date, float]


def load_prices(ticker: str, start_date: date, end_date: date) -> PriceMap:
    # Fetch one extra day so yfinance's exclusive end date includes end_date
    df = yf.download(
        ticker,
        start=start_date.isoformat(),
        end=(end_date + timedelta(days=1)).isoformat(),
        auto_adjust=True,
        progress=False,
    )

    if df.empty:
        return {}

    prices: PriceMap = {}
    for ts, row in df.iterrows():
        d = ts.date() if hasattr(ts, "date") else date.fromisoformat(str(ts)[:10])
        close = row["Close"]
        if hasattr(close, "item"):
            close = close.item()
        prices[d] = float(close)

    return prices


def nearest_price(
    prices: PriceMap, target_date: date, max_lookahead: int = 5
) -> float | None:
    """
    Returns the closing price on target_date, or the next available trading day
    within max_lookahead days. Used for exit prices. Handles weekends and holidays.
    """
    for offset in range(max_lookahead + 1):
        d = target_date + timedelta(days=offset)
        if d in prices:
            return prices[d]
    return None


def nearest_price_backward(
    prices: PriceMap, target_date: date, max_lookback: int = 7
) -> float | None:
    """
    Returns the closing price on target_date, or the most recent available trading
    day within max_lookback days. Used for entry prices when today is a weekend
    or holiday and the market has not yet opened.
    """
    for offset in range(max_lookback + 1):
        d = target_date - timedelta(days=offset)
        if d in prices:
            return prices[d]
    return None
