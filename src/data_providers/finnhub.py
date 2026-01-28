from collections.abc import Iterable
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Union

from finnhub import Client

from .base import BaseClient


class FinnHubAPIClient(BaseClient):
    """
    Thin Python wrapper for FinnHubAPIClient. Converts SDK objects to plain
    dictionaries and returns metadata in a JSON-friendly structure.
    """

    def __init__(self, api_key: str):
        self.client = Client(api_key=api_key)
        self.provider = "finnhub"

    def company_basic_financials(self, ticker: str, metric: str = "all"):
        """
        Provides company financials data.
        Args:
            ticker (str): Stock ticker symbol, e.g., 'LLY'
            metric (str): Financial metric to retrieve, e.g., 'all', 'income-statement', 'balance-sheet', 'cash-flow'
        """
        return self._call(
            self.client,
            self.provider,
            "company_basic_financials",
            symbol=ticker,
            metric=metric,
        )

    def company_earnings(self, ticker: str, limit: int | None = None):
        """
        Provides company earnings data.
        Args:
            ticker (str): Stock ticker symbol, e.g., 'AAPL'
            limit (int | None): Number of records to retrieve
        """
        return self._call(
            self.client, self.provider, "company_earnings", symbol=ticker, limit=limit
        )

    def company_news(self, ticker: str, from_: str | date, to: str | date):
        """
        Provides recent company news.

        Args:

            ticker (str): Stock ticker symbol, e.g., 'AAPL'
            from_ (str | date): Start date for news retrieval in 'YYYY-MM-DD'
        """
        return self._call(
            self.client,
            self.provider,
            "company_news",
            symbol=ticker,
            _from=from_,
            to=to,
        )

    def company_peers(self, ticker: str):
        return self._call(self.client, self.provider, "company_peers", symbol=ticker)

    def company_profile2(self, ticker: str):
        return self._call(self.client, self.provider, "company_profile2", symbol=ticker)

    def country(self):
        return self._call(self.client, self.provider, "country")

    def covid19(self):
        return self._call(self.client, self.provider, "covid19")

    def crypto_exchanges(self):
        return self._call(self.client, self.provider, "crypto_exchanges")

    def crypto_symbols(self, exchange: str):
        """
        Args:
            exchange (str): Exchange symbol, e.g., 'BINANCE'
        """
        return self._call(
            self.client, self.provider, "crypto_symbols", exchange=exchange
        )

    def earnings_calendar(
        self,
        from_: str | date,
        to: str | date,
        ticker: str = "",
        international: bool = False,
    ):
        return self._call(
            self.client,
            self.provider,
            "earnings_calendar",
            _from=from_,
            to=to,
            symbol=ticker,
        )

    def fda_calendar(self):
        return self._call(self.client, self.provider, "fda_calendar")

    def filings(self, ticker: str, from_: str | date, to: str | date):
        return self._call(
            self.client, self.provider, "filings", symbol=ticker, _from=from_, to=to
        )

    def financials_reported(self, ticker: str, freq: str = "annual"):
        return self._call(
            self.client, self.provider, "financials_reported", symbol=ticker, freq=freq
        )

    def forex_exchanges(self):
        return self._call(self.client, self.provider, "forex_exchanges")

    def forex_symbols(self, exchange: str):
        """
        Args:
            exchange (str): Exchange symbol, e.g., 'OANDA'
        """
        return self._call(
            self.client, self.provider, "forex_symbols", exchange=exchange
        )

    def general_news(self, category: str, min_id: int = 0):
        """
        Args:
            category (str): Category of news, e.g., 'general', 'forex', 'crypto'
            min_id (int): Minimum news ID to fetch news after this ID
        """
        return self._call(
            self.client, self.provider, "general_news", category=category, min_id=min_id
        )

    def ipo_calendar(self, from_: str | date, to: str | date):
        return self._call(
            self.client, self.provider, "ipo_calendar", _from=from_, to=to
        )

    def quote(self, ticker: str):
        return self._call(self.client, self.provider, "quote", symbol=ticker)

    def recommendation_trends(self, ticker: str):
        return self._call(
            self.client, self.provider, "recommendation_trends", symbol=ticker
        )

    def stock_insider_sentiment(self, ticker: str, from_: str | date, to: str | date):
        return self._call(
            self.client,
            self.provider,
            "stock_insider_sentiment",
            symbol=ticker,
            _from=from_,
            to=to,
        )

    def stock_insider_transactions(
        self, ticker: str, from_: str | date | None = None, to: str | date | None = None
    ):
        return self._call(
            self.client,
            self.provider,
            "stock_insider_transactions",
            symbol=ticker,
            _from=from_,
            to=to,
        )

    def stock_lobbying(self, ticker: str, from_: str | date, to: str | date):
        return self._call(
            self.client,
            self.provider,
            "stock_lobbying",
            symbol=ticker,
            _from=from_,
            to=to,
        )

    def stock_usa_spending(self, ticker: str, from_: str | date, to: str | date):
        return self._call(
            self.client,
            self.provider,
            "stock_usa_spending",
            symbol=ticker,
            _from=from_,
            to=to,
        )

    def stock_uspto_patent(
        self, ticker: str, from_: str | date | None = None, to: str | date | None = None
    ):
        return self._call(
            self.client,
            self.provider,
            "stock_uspto_patent",
            symbol=ticker,
            _from=from_,
            to=to,
        )

    def stock_visa_application(
        self, ticker: str, from_: str | date | None = None, to: str | date | None = None
    ):
        return self._call(
            self.client,
            self.provider,
            "stock_visa_application",
            symbol=ticker,
            _from=from_,
            to=to,
        )

    def symbol_lookup(self, ticker: str):
        return self._call(self.client, self.provider, "symbol_lookup", query=ticker)
