from collections.abc import Iterable
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Union

from massive import RESTClient


class MassiveAPIClient:
    """
    Thin Python wrapper for MassiveAPIClient. Converts SDK objects to plain
    dictionaries and returns metadata in a JSON-friendly structure.
    """

    def __init__(self, api_key: str):
        self.api_key = RESTClient(api_key=api_key)

    def _serialize(self, obj: Any) -> Any:
        if obj is None:
            return None
        if isinstance(obj, (dict, str, bytes)):
            return obj
        if isinstance(obj, Iterable):
            out = []
            for v in obj:
                if isinstance(v, dict):
                    out.append(v)
                elif hasattr(v, "__dict__"):
                    out.append(
                        {k: getattr(v, k) for k in v.__dict__ if not k.startswith("_")}
                    )
                else:
                    out.append(v)
            return out
        if hasattr(obj, "__dict__"):
            return {k: getattr(obj, k) for k in obj.__dict__ if not k.startswith("_")}
        return obj

    def _make_response(
        self, endpoint: str, result: Any, extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        payload = {
            "provider": "massive",
            "endpoint": endpoint,
            "fetched_at": datetime.now().isoformat(sep=" "),
            "raw": self._serialize(result),
        }
        if extra:
            payload.update(extra)
        return payload

    def _call(self, endpoint: str, *args, **kwargs) -> Dict[str, Any]:
        try:
            func = getattr(self.api_key, endpoint)
            result = func(*args, **kwargs)
            extra = {}
            if "ticker" in kwargs:
                extra["ticker"] = kwargs.get("ticker")
            elif args and isinstance(args[0], str):
                extra["ticker"] = args[0]
            return self._make_response(endpoint, result, extra=extra)
        except Exception as e:
            resp = {
                "provider": "massive",
                "endpoint": endpoint,
                "fetched_at": datetime.now().isoformat(sep=" "),
                "raw": [],
                "error": str(e),
            }
            if "ticker" in kwargs:
                resp["ticker"] = kwargs.get("ticker")
            return resp

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
            "get_daily_open_close_agg", ticker=ticker, date=date, adjusted=adjusted
        )

    def get_ema(self, ticker: str, *args, **kwargs) -> dict:
        """
        IndicatorsClient
        """
        return self._call("get_ema", ticker=ticker, *args, **kwargs)

    def get_exchanges(self, asset_class: str | None, *args, **kwargs) -> dict:
        """
        ExchangesClient
        """
        return self._call("get_exchanges", asset_class=asset_class, *args, **kwargs)

    def get_macd(self, ticker: str, *args, **kwargs) -> dict:
        """
        IndicatorsClient
        """
        return self._call("get_macd", ticker=ticker, *args, **kwargs)

    def get_market_holidays(self, params: dict | None = None, *args, **kwargs) -> dict:
        """
        MarketsClient
        """
        return self._call("get_market_holidays", params=params, *args, **kwargs)

    def get_market_status(self, params: dict | None = None, *args, **kwargs) -> dict:
        """
        MarketsClient
        """
        return self._call("get_market_status", params=params, *args, **kwargs)

    def get_previous_close_agg(self, ticker: str) -> dict:
        """
        AggsClient
        """
        return self._call("get_previous_close_agg", ticker=ticker)

    def get_related_companies(self, ticker: str) -> dict:
        """
        TickersClient
        """
        return self._call("get_related_companies", ticker=ticker)

    def get_rsi(self, ticker: str, *args, **kwargs) -> dict:
        """
        IndicatorsClient
        """
        return self._call("get_rsi", ticker=ticker, *args, **kwargs)

    def get_sma(self, ticker: str, *args, **kwargs) -> dict:
        """
        IndicatorsClient
        """
        return self._call("get_sma", ticker=ticker, *args, **kwargs)

    def get_ticker_details(self, ticker: str, date: str | date | None = None) -> dict:
        """
        TickersClient
        """
        return self._call("get_ticker_details", ticker=ticker, date=date)

    def get_ticker_events(self, ticker: str, type: str | None = None) -> dict:
        """
        TickersClient
        """
        return self._call("get_ticker_events", ticker=ticker, type=type)

    def get_ticker_types(self, asset_class: str | None = None, *args, **kwargs) -> dict:
        """
        TickersClient
        """
        return self._call("get_ticker_types", asset_class=asset_class, *args, **kwargs)

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
        return self._call("list_conditions", asset_class=asset_class, *args, **kwargs)

    def list_dividends(self, ticker: str, *args, **kwargs) -> dict:
        """
        DividendsCLient
        """
        return self._call("list_dividends", ticker=ticker, *args, **kwargs)

    def list_inflation(
        self, date: str | date | None = None, limit: int | None = None, *args, **kwargs
    ) -> dict:
        """
        EconomyClient
        """
        return self._call("list_inflation", date=date, limit=limit, *args, **kwargs)

    def list_options_contracts(
        self, underlying_ticker: str | None = None, *args, **kwargs
    ) -> dict:
        """
        ContractsClient
        """
        return self._call(
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
            "list_short_interest", ticker=ticker, limit=limit, *args, **kwargs
        )

    def list_short_volume(
        self, ticker: str | None = None, date: str | date | None = None, *args, **kwargs
    ) -> dict:
        """
        ContractsClient
        """
        return self._call(
            "list_short_volume", ticker=ticker, date=date, *args, **kwargs
        )

    def list_splits(
        self, ticker: str | None = None, limit: int | None = None, *args, **kwargs
    ) -> dict:
        """
        SplitsClient
        """
        return self._call("list_splits", ticker=ticker, limit=limit, *args, **kwargs)

    def list_ticker_news(
        self, ticker: str | None = None, limit: int | None = None, *args, **kwargs
    ) -> dict:
        """
        TickersClient
        """
        return self._call(
            "list_ticker_news", ticker=ticker, limit=limit, *args, **kwargs
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
            "list_tickers", ticker=ticker, date=date, limit=limit, *args, **kwargs
        )

    def list_treasury_yields(
        self, date: str | None = None, limit: int | None = None, *args, **kwargs
    ) -> dict:
        """
        EconomyClient
        """
        return self._call(
            "list_treasury_yields", date=date, limit=limit, *args, **kwargs
        )
