import json
import os
from datetime import date, datetime, timezone
from typing import Any

import requests
from redis import Redis

redis_client = Redis(
    host="localhost",
    port=6379,
    db=0,
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True,
)


class MarketStackAPIClient:
    """
    Thin Python wrapper for MarketStack API.
    No BaseClient inheritance due to direct requests usage.
    Redis used to cache responses, since MarketStack free tier has rate limits.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._url = "https://api.marketstack.com/v2/"
        self.provider = "marketstack"
        self.cache_ttl = 604800  # config.py?

    def _wrap_response(self, data: Any, ticker: str, endpoint: str) -> dict:
        try:
            payload = {
                "provider": self.provider,
                "endpoint": endpoint,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "data": data,
                "ok": True,
                "ticker": ticker,
            }
            return payload
        except Exception as e:
            resp = {
                "provider": self.provider,
                "endpoint": endpoint,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "data": [],
                "ok": False,
                "error": str(e),
                "ticker": ticker,
            }
            return resp

    def eod_data(
        self, ticker: str, date_from: str | None = None, date_to: str | None = None
    ):
        endpoint = "end_of_day"

        if date_from or date_to:
            cache_key = f"marketstack:eod:{ticker}:{date_from}:{date_to}"
        else:
            cache_key = f"marketstack:eod:{ticker}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
                "symbols": ticker,
            }
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to

            url = f"{self._url}eod"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, ticker, endpoint)

    def eod_latest_data(self, ticker: str):
        endpoint = "end_of_day_latest"

        cache_key = f"marketstack:eod_latest:{ticker}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            url = f"{self._url}eod/latest"
            params = {
                "access_key": self.api_key,
                "symbols": ticker,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

        return self._wrap_response(data, ticker, endpoint)

    def eod_data_specific_date(self, date: str, ticker: str):
        endpoint = "end_of_day_specific_date"

        cache_key = f"marketstack:eod_specific_date:{ticker}:{date}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
                "symbols": ticker,
            }
            url = f"{self._url}eod/{date}"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, ticker, endpoint)

    def splits_data(
        self, ticker: str, date_from: str | None = None, date_to: str | None = None
    ):
        endpoint = "splits_data"

        if date_from or date_to:
            cache_key = f"marketstack:splits_data:{ticker}:{date_from}:{date_to}"
        else:
            cache_key = f"marketstack:splits_data:{ticker}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
                "symbols": ticker,
            }
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to

            url = f"{self._url}splits"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, ticker, endpoint)

    def dividends_data(
        self, ticker: str, date_from: str | None = None, date_to: str | None = None
    ):
        endpoint = "dividends_data"

        if date_from or date_to:
            cache_key = f"marketstack:dividends_data:{ticker}:{date_from}:{date_to}"
        else:
            cache_key = f"marketstack:dividends_data:{ticker}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
                "symbols": ticker,
            }
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to

            url = f"{self._url}dividends"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, ticker, endpoint)

    def ticker_information(self, ticker: str):
        endpoint = "ticker_information"

        cache_key = f"marketstack:ticker_information:{ticker}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }

            url = f"{self._url}tickers/{ticker}"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, ticker, endpoint)

    def eod_data_specific_ticker(self, ticker: str):
        endpoint = "end_of_day_specific_ticker"

        cache_key = f"marketstack:eod_specific_ticker:{ticker}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            url = f"{self._url}tickers/{ticker}/eod"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, ticker, endpoint)

    def splits_factor_specific_ticker(
        self, ticker: str, date_from: str | None = None, date_to: str | None = None
    ):
        endpoint = "splits_factor_specific_ticker"

        if date_from or date_to:
            cache_key = f"marketstack:splits_factor_specific_ticker:{ticker}:{date_from}:{date_to}"
        else:
            cache_key = f"marketstack:splits_factor_specific_ticker:{ticker}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to
            url = f"{self._url}tickers/{ticker}/splits"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))
            return self._wrap_response(data, ticker, endpoint)

    def dividends_data_specific_ticker(
        self, ticker: str, date_from: str | None = None, date_to: str | None = None
    ):
        endpoint = "dividends_data_specific_ticker"

        if date_from or date_to:
            cache_key = f"marketstack:dividends_data_specific_ticker:{ticker}:{date_from}:{date_to}"
        else:
            cache_key = f"marketstack:dividends_data_specific_ticker:{ticker}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to
            url = f"{self._url}tickers/{ticker}/dividends"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))
            return self._wrap_response(data, ticker, endpoint)

    def eod_specific_ticker_specific_date(self, ticker: str, date: str):
        endpoint = "eod_specific_ticker_specific_date"

        cache_key = f"marketstack:eod_specific_ticker_specific_date:{ticker}:{date}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            url = f"{self._url}tickers/{ticker}/eod/{date}"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, ticker, endpoint)

    def eod_latest_data_specific_ticker(self, ticker: str):
        endpoint = "eod_latest_data_specific_ticker"

        cache_key = f"marketstack:eod_latest_data_specific_ticker:{ticker}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), ticker, endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            url = f"{self._url}tickers/{ticker}/eod/latest"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, ticker, endpoint)

    def tickers_list(self):
        endpoint = "tickers_list"

        cache_key = f"marketstack:tickers_list"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), "", endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            url = f"{self._url}tickerslist"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, "", endpoint)

    def exchanges(self):
        endpoint = "exchanges"

        cache_key = f"marketstack:exchanges"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), "", endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            url = f"{self._url}exchanges"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, "", endpoint)

    def specific_stock_exchange_info(self, mic: str):
        """
        Args:
            mic (str): Market Identifier Code of the exchange (e,g., 'XNAS')
        """
        endpoint = "specific_stock_exchange_info"

        cache_key = f"marketstack:specific_stock_exchange_info:{mic}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), "", endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            url = f"{self._url}exchanges/{mic}"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, "", endpoint)

    def specific_stock_exchange_ticker(self, mic: str):
        """
        Args:
            mic (str): Market Identifier Code of the exchange (e,g., 'XNAS')
        """
        endpoint = "specific_stock_exchange_ticker"

        cache_key = f"marketstack:specific_stock_exchange_ticker:{mic}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), "", endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            url = f"{self._url}exchanges/{mic}/tickers"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, "", endpoint)

    def eod_data_specific_stock_exchange(
        self,
        mic: str,
        ticker: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ):
        """
        Args:
            mic (str): Market Identifier Code of the exchange (e,g., 'XNAS')
            ticker (str): Ticker symbol of the stock
            date_from (str | None): Start date in 'YYYY-MM-DD' format
            date_to (str | None): End date in 'YYYY-MM-DD' format
        """
        endpoint = "eod_data_specific_stock_exchange"

        if date_from or date_to:
            cache_key = f"marketstack:eod_data_specific_stock_exchange:{mic}:{ticker}:{date_from}:{date_to}"
        else:
            cache_key = f"marketstack:eod_data_specific_stock_exchange:{mic}:{ticker}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), "", endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
                "symbols": ticker,
            }
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to
            url = f"{self._url}exchanges/{mic}/eod"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, "", endpoint)

    def eod_data_latest_date_specific_stock_exchange(self, mic: str, ticker: str):
        """
        Args:
            mic (str): Market Identifier Code of the exchange (e,g., 'XNAS')
            ticker (str): Ticker symbol of the stock
        """
        endpoint = "eod_data_latest_date_specific_stock_exchange"

        cache_key = (
            f"marketstack:eod_data_latest_date_specific_stock_exchange:{mic}:{ticker}"
        )
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), "", endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
                "symbols": ticker,
            }
            url = f"{self._url}exchanges/{mic}/eod/latest"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, "", endpoint)

    def eod_data_specific_stock_exchange_specific_date(
        self, mic: str, ticker: str, date: str
    ):
        """
        Args:
            mic (str): Market Identifier Code of the exchange (e,g., 'XNAS')
            ticker (str): Ticker symbol of the stock
            date (str): Specific date in 'YYYY-MM-DD' format
        """
        endpoint = "eod_data_specific_stock_exchange_specific_date"

        cache_key = f"marketstack:eod_data_specific_stock_exchange_specific_date:{mic}:{ticker}:{date}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), "", endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
                "symbols": ticker,
            }
            url = f"{self._url}exchanges/{mic}/eod/{date}"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, "", endpoint)

    def currencies(self):
        endpoint = "currencies"

        cache_key = f"marketstack:currencies"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return self._wrap_response(json.loads(cached_data), "", endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            url = f"{self._url}currencies"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, "", endpoint)

    def timezones(self):
        endpoint = "timezones"

        cache_key = f"marketstack:timezones"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            print(cached_data)
            return self._wrap_response(json.loads(cached_data), "", endpoint)  # type: ignore
        else:
            params = {
                "access_key": self.api_key,
            }
            url = f"{self._url}timezones"
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

            return self._wrap_response(data, "", endpoint)
