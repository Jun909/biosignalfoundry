"""
Tests for the Redis caching layer in src/data_providers/*.py.

Mocking strategy
-----------------
Each provider module imports its own `redis_client` reference, so we patch
`get`/`setex` on that reference directly (the same seam test_app_analyze.py
uses for app.py's cache).

For finnhub/alphavantage, the upstream SDK call is routed through
BaseClient._call, so we patch the client instance's `_call` method instead
of the underlying SDK — this avoids needing real API responses.

For marketstack there is no BaseClient; it calls `requests.get` directly,
so we patch `requests.get` in that module instead.

marketstack.py has ~20 near-identical cache/method pairs (see
src/data_providers/marketstack.py); rather than duplicating the same test
20 times, we exercise the shared pattern through one representative method
(`ticker_information`).
"""

import json
from unittest.mock import MagicMock, patch

from redis.exceptions import ConnectionError as RedisConnectionError

import src.data_providers.alphavantage as alphavantage_module
import src.data_providers.finnhub as finnhub_module
import src.data_providers.marketstack as marketstack_module
from config import (REDIS_CACHE_TTL_SECONDS_ALPHAVANTAGE,
                    REDIS_CACHE_TTL_SECONDS_ALPHAVANTAGE_ERROR,
                    REDIS_CACHE_TTL_SECONDS_FINNHUB,
                    REDIS_CACHE_TTL_SECONDS_MARKETSTACK)
from src.data_providers.alphavantage import AlphaVantageAPIClient
from src.data_providers.finnhub import FinnHubAPIClient
from src.data_providers.marketstack import MarketStackAPIClient

# ---------------------------------------------------------------------------
# finnhub.py — company_profile2
# ---------------------------------------------------------------------------


class TestFinnHubCompanyProfile2:
    def setup_method(self):
        self.client = FinnHubAPIClient(api_key="dummy")
        self.client._call = MagicMock(
            return_value={"ok": True, "data": {"name": "NVIDIA"}}
        )

    def test_cache_hit_skips_api_call(self):
        cached = {"ok": True, "data": {"name": "NVIDIA"}}
        with patch.object(
            finnhub_module.redis_client, "get", return_value=json.dumps(cached)
        ):
            result = self.client.company_profile2("NVDA")

        assert result == cached
        self.client._call.assert_not_called()

    def test_cache_miss_calls_api_and_writes_cache(self):
        with (
            patch.object(finnhub_module.redis_client, "get", return_value=None),
            patch.object(finnhub_module.redis_client, "setex") as mock_setex,
        ):
            result = self.client.company_profile2("NVDA")

        assert result == {"ok": True, "data": {"name": "NVIDIA"}}
        mock_setex.assert_called_once_with(
            "finnhub:company_profile2:NVDA",
            REDIS_CACHE_TTL_SECONDS_FINNHUB,
            json.dumps(result),
        )

    def test_redis_read_failure_falls_back_to_cache_miss(self):
        with (
            patch.object(
                finnhub_module.redis_client,
                "get",
                side_effect=RedisConnectionError("down"),
            ),
            patch.object(finnhub_module.redis_client, "setex") as mock_setex,
        ):
            result = self.client.company_profile2("NVDA")

        assert result == {"ok": True, "data": {"name": "NVIDIA"}}
        self.client._call.assert_called_once()
        mock_setex.assert_called_once()

    def test_redis_write_failure_still_returns_result(self):
        with (
            patch.object(finnhub_module.redis_client, "get", return_value=None),
            patch.object(
                finnhub_module.redis_client,
                "setex",
                side_effect=RedisConnectionError("down"),
            ),
        ):
            result = self.client.company_profile2("NVDA")

        assert result == {"ok": True, "data": {"name": "NVIDIA"}}


# ---------------------------------------------------------------------------
# alphavantage.py — get_income_statement_annual
# ---------------------------------------------------------------------------


class TestAlphaVantageIncomeStatementAnnual:
    def setup_method(self):
        self.client = AlphaVantageAPIClient(api_key="dummy")
        self.client._call = MagicMock(
            return_value={"ok": True, "ticker": "NVDA", "data": [[]]}
        )

    def test_cache_hit_skips_api_call(self):
        cached = {"ok": True, "ticker": "NVDA", "data": [[]]}
        with patch.object(
            alphavantage_module.redis_client, "get", return_value=json.dumps(cached)
        ):
            result = self.client.get_income_statement_annual("NVDA")

        assert result == cached
        self.client._call.assert_not_called()

    def test_cache_miss_writes_success_ttl(self):
        with (
            patch.object(alphavantage_module.redis_client, "get", return_value=None),
            patch.object(alphavantage_module.redis_client, "setex") as mock_setex,
        ):
            result = self.client.get_income_statement_annual("NVDA")

        assert result == {"ok": True, "ticker": "NVDA", "data": [[]]}
        mock_setex.assert_called_once_with(
            "alphavantage:get_income_statement_annual:NVDA",
            REDIS_CACHE_TTL_SECONDS_ALPHAVANTAGE,
            json.dumps(result),
        )

    def test_cache_miss_writes_error_ttl_on_api_failure(self):
        self.client._call.return_value = {"ok": False, "error": "rate limited"}
        with (
            patch.object(alphavantage_module.redis_client, "get", return_value=None),
            patch.object(alphavantage_module.redis_client, "setex") as mock_setex,
        ):
            self.client.get_income_statement_annual("NVDA")

        mock_setex.assert_called_once_with(
            "alphavantage:get_income_statement_annual:NVDA",
            REDIS_CACHE_TTL_SECONDS_ALPHAVANTAGE_ERROR,
            json.dumps({"ok": False, "error": "rate limited"}),
        )

    def test_redis_read_failure_falls_back_to_cache_miss(self):
        with (
            patch.object(
                alphavantage_module.redis_client,
                "get",
                side_effect=RedisConnectionError("down"),
            ),
            patch.object(alphavantage_module.redis_client, "setex") as mock_setex,
        ):
            result = self.client.get_income_statement_annual("NVDA")

        assert result == {"ok": True, "ticker": "NVDA", "data": [[]]}
        self.client._call.assert_called_once()
        mock_setex.assert_called_once()

    def test_redis_write_failure_still_returns_result(self):
        with (
            patch.object(alphavantage_module.redis_client, "get", return_value=None),
            patch.object(
                alphavantage_module.redis_client,
                "setex",
                side_effect=RedisConnectionError("down"),
            ),
        ):
            result = self.client.get_income_statement_annual("NVDA")

        assert result == {"ok": True, "ticker": "NVDA", "data": [[]]}


# ---------------------------------------------------------------------------
# marketstack.py — ticker_information (representative of ~20 identical
# cache/method pairs; see module docstring above)
# ---------------------------------------------------------------------------


class TestMarketStackTickerInformation:
    def setup_method(self):
        self.client = MarketStackAPIClient(api_key="dummy")

    def _mock_response(self, payload):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = payload
        return resp

    def test_cache_hit_skips_http_call(self):
        cached_payload = {"name": "NVIDIA Corp"}
        with (
            patch.object(
                marketstack_module.redis_client,
                "get",
                return_value=json.dumps(cached_payload),
            ),
            patch.object(marketstack_module.requests, "get") as mock_get,
        ):
            result = self.client.ticker_information("NVDA")

        assert result["ok"] is True
        assert result["data"] == cached_payload
        mock_get.assert_not_called()

    def test_cache_miss_calls_api_and_writes_cache(self):
        payload = {"name": "NVIDIA Corp"}
        with (
            patch.object(marketstack_module.redis_client, "get", return_value=None),
            patch.object(marketstack_module.redis_client, "setex") as mock_setex,
            patch.object(
                marketstack_module.requests,
                "get",
                return_value=self._mock_response(payload),
            ) as mock_get,
        ):
            result = self.client.ticker_information("NVDA")

        assert result["ok"] is True
        assert result["data"] == payload
        mock_get.assert_called_once()
        mock_setex.assert_called_once_with(
            "marketstack:ticker_information:NVDA",
            REDIS_CACHE_TTL_SECONDS_MARKETSTACK,
            json.dumps(payload),
        )

    def test_redis_read_failure_falls_back_to_cache_miss(self):
        payload = {"name": "NVIDIA Corp"}
        with (
            patch.object(
                marketstack_module.redis_client,
                "get",
                side_effect=RedisConnectionError("down"),
            ),
            patch.object(marketstack_module.redis_client, "setex") as mock_setex,
            patch.object(
                marketstack_module.requests,
                "get",
                return_value=self._mock_response(payload),
            ) as mock_get,
        ):
            result = self.client.ticker_information("NVDA")

        assert result["ok"] is True
        assert result["data"] == payload
        mock_get.assert_called_once()
        mock_setex.assert_called_once()

    def test_redis_write_failure_still_returns_result(self):
        payload = {"name": "NVIDIA Corp"}
        with (
            patch.object(marketstack_module.redis_client, "get", return_value=None),
            patch.object(
                marketstack_module.redis_client,
                "setex",
                side_effect=RedisConnectionError("down"),
            ),
            patch.object(
                marketstack_module.requests,
                "get",
                return_value=self._mock_response(payload),
            ),
        ):
            result = self.client.ticker_information("NVDA")

        assert result["ok"] is True
        assert result["data"] == payload
