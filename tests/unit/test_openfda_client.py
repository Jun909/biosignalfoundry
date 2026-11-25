from unittest.mock import MagicMock, patch

import pytest
import requests

from src.data_providers.openfda import (Dataset, OpenFDAAPIClient, Query,
                                        SearchClause)

KEY = "secret-key-123"


@pytest.fixture(autouse=True)
def no_redis():
    """Keep these tests off the network: every call is a cache miss, writes are no-ops."""
    with patch("src.data_providers.cache.redis_client") as redis:
        redis.get.return_value = None
        yield redis


def _response(status: int, body: dict | None = None):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = body or {}
    if status >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(
            f"{status} Error for url: https://api.fda.gov/x?api_key={KEY}"
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


def _client():
    return OpenFDAAPIClient(api_key=KEY)


def test_no_match_404_is_ok_with_empty_results():
    with patch("requests.get", return_value=_response(404)):
        out = _client().query(Dataset.DRUG_FDA, Query(limit=1))
    assert out["ok"] is True
    assert out["data"]["results"] == []


def test_real_error_is_not_ok_and_does_not_leak_api_key():
    body = {"error": {"message": "Bad query"}}
    with patch("requests.get", return_value=_response(500, body)):
        out = _client().query(Dataset.DRUG_FDA, Query(limit=1))
    assert out["ok"] is False
    assert KEY not in out["error"]
    assert "Bad query" in out["error"]


def test_network_error_does_not_leak_api_key():
    with patch(
        "requests.get",
        side_effect=requests.ConnectionError(f"failed for api_key={KEY}"),
    ):
        out = _client().query(Dataset.DRUG_FDA, Query(limit=1))
    assert out["ok"] is False
    assert KEY not in out["error"]


def test_plus_separators_and_wildcards_are_not_url_encoded():
    query = Query(
        search=[
            SearchClause("sponsor_name", "VERTEX*"),
            SearchClause("submissions.submission_status", "AP"),
        ],
        limit=3,
    )
    with patch("requests.get", return_value=_response(200, {"results": []})) as get:
        _client().query(Dataset.DRUG_FDA, query)
    url = get.call_args.args[0]
    assert "search=sponsor_name:VERTEX*+AND+submissions.submission_status:AP" in url
    assert "%2B" not in url


def test_date_range_term_is_kept_intact():
    query = Query(
        search=[SearchClause("letter_date", "[20250101+TO+20251231]")], limit=1
    )
    with patch("requests.get", return_value=_response(200, {"results": []})) as get:
        _client().query(Dataset.TRANSPARENCY, query)
    assert "[20250101+TO+20251231]" in get.call_args.args[0]


def _page(total: int, n: int):
    return _response(
        200,
        {
            "meta": {"results": {"total": total}},
            "results": [{"i": i} for i in range(n)],
        },
    )


def test_truncated_flag_when_total_exceeds_returned():
    with patch("requests.get", return_value=_page(total=250, n=100)):
        out = _client().query(Dataset.DRUG_FDA, Query(limit=100))
    assert out["total"] == 250
    assert out["truncated"] is True


def test_not_truncated_when_everything_returned():
    with patch("requests.get", return_value=_page(total=10, n=10)):
        out = _client().query(Dataset.DRUG_FDA, Query(limit=100))
    assert out["truncated"] is False


def test_query_all_pages_until_total_reached():
    pages = [_page(250, 100), _page(250, 100), _page(250, 50)]
    with patch("requests.get", side_effect=pages) as get:
        out = _client().query_all(Dataset.DRUG_FDA, Query(limit=100), max_records=1000)
    assert len(out["data"]["results"]) == 250
    assert out["truncated"] is False
    assert get.call_count == 3
    assert "skip=100" in get.call_args_list[1].args[0]


def test_query_all_flags_truncation_at_max_records():
    with patch("requests.get", side_effect=[_page(5000, 100), _page(5000, 100)]):
        out = _client().query_all(Dataset.DRUG_FDA, Query(), max_records=200)
    assert len(out["data"]["results"]) == 200
    assert out["truncated"] is True


def test_successful_response_is_cached_and_failure_is_not(no_redis):
    with patch("requests.get", return_value=_page(1, 1)):
        _client().query(Dataset.DRUG_FDA, Query(limit=1))
    assert no_redis.setex.call_count == 1

    no_redis.setex.reset_mock()
    with patch("requests.get", return_value=_response(500)):
        _client().query(Dataset.DRUG_FDA, Query(limit=1))
    no_redis.setex.assert_not_called()


def test_cache_hit_skips_the_request(no_redis):
    cached = {"ok": True, "data": {"results": []}}
    no_redis.get.return_value = __import__("json").dumps(cached)
    with patch("requests.get") as get:
        out = _client().query(Dataset.DRUG_FDA, Query(limit=1))
    assert out == cached
    get.assert_not_called()


def test_error_has_the_standard_shape():
    with patch("requests.get", return_value=_response(500)):
        out = _client().query(Dataset.DRUG_FDA, Query(limit=1))
    assert {"provider", "endpoint", "fetched_at", "data", "ok", "error"} <= out.keys()
    assert out["endpoint"] == "drug/drugsfda"


def test_company_search_keys_handle_hyphens_and_digits():
    from src.data_providers.openfda import company_search_keys

    assert company_search_keys("Intra-Cellular Therapies Inc") == [
        "INTRACELLULAR",
        "INTRA",
    ]
    assert company_search_keys("Moderna, Inc.") == ["MODERNA"]
    assert company_search_keys("89bio, Inc.") == ["89BIO"]
    assert company_search_keys("") == []


def test_matches_company_requires_whole_word_prefix():
    from src.data_providers.openfda import matches_company

    assert matches_company("Intra-Cellular Therapies Inc", "INTRA-CELLULAR")
    assert matches_company("Biogen Inc.", "BIOGEN IDEC INC")
    assert matches_company("Vertex Pharmaceuticals Incorporated", "VERTEX PHARMS")
    assert not matches_company("Intra-Cellular Therapies Inc", "INTRABIO")
    assert not matches_company("Biogen Inc.", "BIOGENERIX")
    assert not matches_company("Biogen Inc.", "")
