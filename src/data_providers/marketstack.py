import json
import requests
from datetime import datetime, timezone
from redis import Redis
import os
from typing import Any

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
        payload = {
            "provider": self.provider,
            "endpoint": endpoint,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
            "ok": True,
            "ticker": ticker,
        }
        return payload

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
