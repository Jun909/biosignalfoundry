import json
from unittest.mock import patch

from src.data_providers.sec_edgar import SECEdgarClient


def _client() -> SECEdgarClient:
    client = SECEdgarClient.__new__(SECEdgarClient)
    client.provider = "sec_edgartools"
    return client


def test_error_has_the_standard_shape_and_is_not_cached():
    with (
        patch("src.data_providers.cache.redis_client") as redis,
        patch("src.data_providers.sec_edgar.Company", side_effect=RuntimeError("boom")),
    ):
        redis.get.return_value = None
        out = _client().get_8k_data("MRNA")

    assert out["ok"] is False
    assert out["error"] == "boom"
    assert {"provider", "endpoint", "fetched_at", "data"} <= out.keys()
    assert out["ticker"] == "MRNA"
    redis.setex.assert_not_called()


def test_8k_result_is_cached_by_ticker_and_limit():
    with (
        patch("src.data_providers.cache.redis_client") as redis,
        patch.object(
            SECEdgarClient,
            "_fetch_8k_data",
            return_value={"ok": True, "data": [], "ticker": "MRNA"},
        ) as fetch,
    ):
        redis.get.return_value = None
        _client().get_8k_data("mrna", limit=3)

    fetch.assert_called_once_with("mrna", 3)
    assert redis.setex.call_args.args[0] == "sec_edgar:8k:MRNA:3"


def test_8k_cache_hit_skips_edgar():
    cached = {"ok": True, "data": [{"accession_number": "x"}]}
    with (
        patch("src.data_providers.cache.redis_client") as redis,
        patch.object(SECEdgarClient, "_fetch_8k_data") as fetch,
    ):
        redis.get.return_value = json.dumps(cached)
        out = _client().get_8k_data("MRNA")

    assert out == cached
    fetch.assert_not_called()
