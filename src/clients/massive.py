from collections.abc import Iterable
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Union

from massive import RESTClient

from .base import BaseClient


class MassiveAPIClient(BaseClient):
    """
    Thin Python wrapper for MassiveAPIClient. Converts SDK objects to plain
    dictionaries and returns metadata in a JSON-friendly structure.
    """

    def __init__(self, api_key: str):
        self.client = RESTClient(api_key=api_key)
        self.provider = "massive"

    def get_aggs(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_: str | int | datetime | date,
        to: str | int | datetime | date,
        adjusted: bool | None = None,
        sort: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        AggsClient
        """
        return self._call(
            self.client,
            self.provider,
            "get_aggs",
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_=from_,
            to=to,
            adjusted=adjusted,
            sort=sort,
            limit=limit,
        )

    def get_daily_open_close_agg(
        self,
        ticker: str,
        date: str | date,
        adjusted: bool | None = None,
    ) -> dict:
        """
        AggsClient
        """
        return self._call(
            self.client,
            self.provider,
            "get_daily_open_close_agg",
            ticker=ticker,
            date=date,
            adjusted=adjusted,
        )

    def get_ema(self, ticker: str, *args, **kwargs) -> dict:
        """
        IndicatorsClient
        """
        return self._call(
            self.client, self.provider, "get_ema", ticker=ticker, *args, **kwargs
        )

    def get_exchanges(self, asset_class: str | None, *args, **kwargs) -> dict:
        """
        ExchangesClient
        """
        return self._call(
            self.client,
            self.provider,
            "get_exchanges",
            asset_class=asset_class,
            *args,
            **kwargs,
        )

    def get_macd(self, ticker: str, *args, **kwargs) -> dict:
        """
        IndicatorsClient
        """
        return self._call(
            self.client, self.provider, "get_macd", ticker=ticker, *args, **kwargs
        )

    def get_market_holidays(self, params: dict | None = None, *args, **kwargs) -> dict:
        """
        MarketsClient
        """
        return self._call(
            self.client,
            self.provider,
            "get_market_holidays",
            params=params,
            *args,
            **kwargs,
        )

    def get_market_status(self, params: dict | None = None, *args, **kwargs) -> dict:
        """
        MarketsClient
        """
        return self._call(
            self.client,
            self.provider,
            "get_market_status",
            params=params,
            *args,
            **kwargs,
        )

    def get_previous_close_agg(self, ticker: str) -> dict:
        """
        AggsClient
        """
        return self._call(
            self.client, self.provider, "get_previous_close_agg", ticker=ticker
        )

    def get_related_companies(self, ticker: str) -> dict:
        """
        TickersClient
        """
        return self._call(
            self.client, self.provider, "get_related_companies", ticker=ticker
        )

    def get_rsi(self, ticker: str, *args, **kwargs) -> dict:
        """
        IndicatorsClient
        """
        return self._call(
            self.client, self.provider, "get_rsi", ticker=ticker, *args, **kwargs
        )

    def get_sma(self, ticker: str, *args, **kwargs) -> dict:
        """
        IndicatorsClient
        """
        return self._call(
            self.client, self.provider, "get_sma", ticker=ticker, *args, **kwargs
        )

    def get_ticker_details(self, ticker: str, date: str | date | None = None) -> dict:
        """
        TickersClient
        """
        return self._call(
            self.client, self.provider, "get_ticker_details", ticker=ticker, date=date
        )

    def get_ticker_events(self, ticker: str, type: str | None = None) -> dict:
        """
        TickersClient
        """
        return self._call(
            self.client, self.provider, "get_ticker_events", ticker=ticker, type=type
        )

    def get_ticker_types(self, asset_class: str | None = None, *args, **kwargs) -> dict:
        """
        TickersClient
        """
        return self._call(
            self.client,
            self.provider,
            "get_ticker_types",
            asset_class=asset_class,
            *args,
            **kwargs,
        )

    def list_aggs(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_: str | int | datetime | date,
        to: str | int | datetime | date,
        limit: int | None = None,
        *args,
        **kwargs,
    ) -> dict:
        """
        AggsClient
        """
        return self._call(
            self.client,
            self.provider,
            "list_aggs",
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_=from_,
            to=to,
            limit=limit,
            *args,
            **kwargs,
        )

    def list_conditions(self, asset_class: str | None = None, *args, **kwargs) -> dict:
        """
        ConditionsClient
        """
        return self._call(
            self.client,
            self.provider,
            "list_conditions",
            asset_class=asset_class,
            *args,
            **kwargs,
        )

    def list_dividends(self, ticker: str, *args, **kwargs) -> dict:
        """
        DividendsCLient
        """
        return self._call(
            self.client, self.provider, "list_dividends", ticker=ticker, *args, **kwargs
        )

    def list_inflation(
        self, date: str | date | None = None, limit: int | None = None, *args, **kwargs
    ) -> dict:
        """
        EconomyClient
        """
        return self._call(
            self.client,
            self.provider,
            "list_inflation",
            date=date,
            limit=limit,
            *args,
            **kwargs,
        )

    def list_options_contracts(
        self, underlying_ticker: str | None = None, *args, **kwargs
    ) -> dict:
        """
        ContractsClient
        """
        return self._call(
            self.client,
            self.provider,
            "list_options_contracts",
            underlying_ticker=underlying_ticker,
            *args,
            **kwargs,
        )

    def list_short_interest(
        self, ticker: str | None = None, limit: int | None = None, *args, **kwargs
    ) -> dict:
        """
        ContractsClient
        """
        return self._call(
            self.client,
            self.provider,
            "list_short_interest",
            ticker=ticker,
            limit=limit,
            *args,
            **kwargs,
        )

    def list_short_volume(
        self, ticker: str | None = None, date: str | date | None = None, *args, **kwargs
    ) -> dict:
        """
        ContractsClient
        """
        return self._call(
            self.client,
            self.provider,
            "list_short_volume",
            ticker=ticker,
            date=date,
            *args,
            **kwargs,
        )

    def list_splits(
        self, ticker: str | None = None, limit: int | None = None, *args, **kwargs
    ) -> dict:
        """
        SplitsClient
        """
        return self._call(
            self.client,
            self.provider,
            "list_splits",
            ticker=ticker,
            limit=limit,
            *args,
            **kwargs,
        )

    def list_ticker_news(
        self, ticker: str | None = None, limit: int | None = None, *args, **kwargs
    ) -> dict:
        """
        TickersClient
        """
        return self._call(
            self.client,
            self.provider,
            "list_ticker_news",
            ticker=ticker,
            limit=limit,
            *args,
            **kwargs,
        )

    def list_tickers(
        self,
        ticker: str | None = None,
        date: str | None = None,
        limit: int | None = None,
        *args,
        **kwargs,
    ) -> dict:
        """
        TickersClient
        """
        return self._call(
            self.client,
            self.provider,
            "list_tickers",
            ticker=ticker,
            date=date,
            limit=limit,
            *args,
            **kwargs,
        )

    def list_treasury_yields(
        self, date: str | None = None, limit: int | None = None, *args, **kwargs
    ) -> dict:
        """
        EconomyClient
        """
        return self._call(
            self.client,
            self.provider,
            "list_treasury_yields",
            date=date,
            limit=limit,
            *args,
            **kwargs,
        )
