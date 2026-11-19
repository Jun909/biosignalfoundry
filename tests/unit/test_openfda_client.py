from unittest.mock import MagicMock, patch

import requests

from src.data_providers.openfda import (Dataset, OpenFDAAPIClient, Query,
                                        SearchClause)

KEY = "secret-key-123"


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
