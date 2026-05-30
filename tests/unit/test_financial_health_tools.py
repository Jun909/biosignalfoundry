"""
Tests for src/agent_tools/financial_health_agent_tools.py.

We split coverage into two layers:

  1. Pure function tests  (_process_income_statement, _process_company_profile)
     No mocking needed — just dict inputs in, dict outputs out.
     These are the most important tests: all tool business logic lives here.

  2. Tool-level smoke tests  (get_income_statement_annual, get_company_profile)
     Mock the module-level API client singletons (avclient, finnclient) so
     the tool's wiring to _process_* is exercised without any HTTP calls.
"""

import pytest
from unittest.mock import patch

import src.agent_tools.financial_health_agent_tools as tools_module
from src.agent_tools.financial_health_agent_tools import (
    _process_company_profile,
    _process_income_statement,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

# A minimal but realistic AlphaVantage income-statement response.
# data[0] is the list of annual records (oldest last, newest first).
VALID_INCOME_RAW = {
    "ok": True,
    "ticker": "NVDA",
    "data": [
        [
            {
                "fiscalDateEnding": "2023-12-31",
                "totalRevenue": "5000000000",            # 5 B → 5.0
                "netIncome": "500000000",                # 0.5 B → 0.5
                "reportedCurrency": "USD",               # non-numeric → kept as-is
                "costofGoodsAndServicesSold": "200000000",  # REDUNDANT → dropped
                "allNullField": None,                    # all-None → dropped
                "anotherNullField": "None",              # all-"None" → dropped
            },
            {
                "fiscalDateEnding": "2022-12-31",
                "totalRevenue": "4000000000",
                "netIncome": "400000000",
                "reportedCurrency": "USD",
                "costofGoodsAndServicesSold": "180000000",
                "allNullField": None,
                "anotherNullField": "None",
            },
            {
                "fiscalDateEnding": "2021-12-31",
                "totalRevenue": "3000000000",
                "netIncome": "300000000",
                "reportedCurrency": "USD",
                "costofGoodsAndServicesSold": "160000000",
                "allNullField": None,
                "anotherNullField": "None",
            },
        ]
    ],
}

VALID_COMPANY_RAW = {
    "ok": True,
    "ticker": "NVDA",
    "data": {
        "name": "NVIDIA Corp",
        "country": "US",
        "currency": "USD",
        "exchange": "NASDAQ",
        "finnhubIndustry": "Semiconductors",
        "ipo": "1999-01-22",
        "marketCapitalization": 1_000_000,
        "shareOutstanding": 24_000_000,
        "weburl": "https://www.nvidia.com/",
        # These must be stripped from the output:
        "irrelevantField": "should be dropped",
        "phone": "+1-555-0000",
    },
}


# ===========================================================================
# 1. _process_income_statement — pure function tests
# ===========================================================================


def test_process_income_statement_api_error_returns_error_dict():
    """
    When the provider signals ok=False the function must return an error
    dict without raising, and include an 'instruction' key telling the
    agent not to retry.

    Why: the agent reads this dict and must be able to decide not to
    hammer the rate-limited API again.
    """
    raw = {"ok": False, "ticker": "FAKE", "error": "rate limit exceeded"}
    result = _process_income_statement(raw, years=5)

    assert result["ok"] is False
    assert result["ticker"] == "FAKE"
    assert "rate limit exceeded" in result["error"]
    assert "instruction" in result, "Agent must be told not to retry"


def test_process_income_statement_empty_data_returns_error_dict():
    """
    ok=True but data=[] (or data=None) must not crash — it should return a
    clean error dict.  The provider sometimes returns an empty payload for
    tickers it doesn't know about.
    """
    raw = {"ok": True, "ticker": "UNKNOWN", "data": None}
    result = _process_income_statement(raw, years=5)

    assert result["ok"] is False
    assert result["ticker"] == "UNKNOWN"
    assert "instruction" in result


def test_process_income_statement_truncates_to_requested_years():
    """
    The function must return at most `years` records even when the raw
    response contains more.  Here we have 3 records and ask for 2.
    """
    result = _process_income_statement(VALID_INCOME_RAW, years=2)

    assert result["ok"] is True
    assert len(result["statements"]) == 2
    assert len(result["fiscal_years"]) == 2
    assert result["fiscal_years"] == ["2023-12-31", "2022-12-31"]


def test_process_income_statement_converts_numeric_fields_to_billions():
    """
    Fields listed in NUMERIC_FIELDS must be divided by 1e9 and rounded to 3
    decimal places so the LLM receives human-readable numbers rather than
    9-digit integers.
    """
    result = _process_income_statement(VALID_INCOME_RAW, years=1)

    stmt = result["statements"][0]
    assert stmt["totalRevenue"] == round(5_000_000_000 / 1e9, 3)   # 5.0
    assert stmt["netIncome"]    == round(  500_000_000 / 1e9, 3)   # 0.5


def test_process_income_statement_keeps_non_numeric_string_fields():
    """
    Fields whose value cannot be parsed as float (e.g. 'USD', '2023-12-31')
    must be kept as plain strings, not discarded.
    """
    result = _process_income_statement(VALID_INCOME_RAW, years=1)

    stmt = result["statements"][0]
    assert stmt.get("reportedCurrency") == "USD"
    assert stmt.get("fiscalDateEnding") == "2023-12-31"


def test_process_income_statement_drops_all_none_columns():
    """
    A column where every record has value None or the string "None" must
    be removed entirely from the output — these add noise for the LLM.
    """
    result = _process_income_statement(VALID_INCOME_RAW, years=3)

    for stmt in result["statements"]:
        assert "allNullField" not in stmt
        assert "anotherNullField" not in stmt


def test_process_income_statement_drops_redundant_fields():
    """
    Fields in REDUNDANT_FIELDS (currently 'costofGoodsAndServicesSold')
    must never appear in the output regardless of their values.
    """
    result = _process_income_statement(VALID_INCOME_RAW, years=3)

    for stmt in result["statements"]:
        assert "costofGoodsAndServicesSold" not in stmt


def test_process_income_statement_metadata_fields_present():
    """
    The output envelope must always include ok, ticker, currency_unit,
    fiscal_years, and statements so downstream consumers can rely on a
    stable schema.
    """
    result = _process_income_statement(VALID_INCOME_RAW, years=2)

    assert result["ok"] is True
    assert result["ticker"] == "NVDA"
    assert result["currency_unit"] == "USD_billions"
    assert isinstance(result["fiscal_years"], list)
    assert isinstance(result["statements"], list)


# ===========================================================================
# 2. _process_company_profile — pure function tests
# ===========================================================================


def test_process_company_profile_api_error_raises_value_error():
    """
    When ok=False the function must raise ValueError containing the ticker
    and a description of the error.

    Why a raise rather than a dict: the agent tool is expected to surface
    this as a tool execution failure so the supervisor can react.
    """
    raw = {"ok": False, "ticker": "FAKE", "error": "symbol not found"}

    with pytest.raises(ValueError) as exc_info:
        _process_company_profile(raw)

    assert "FAKE" in str(exc_info.value)
    assert "symbol not found" in str(exc_info.value)


def test_process_company_profile_keeps_only_allowed_fields():
    """
    Only the keys in COMPANY_PROFILE_FIELDS_TO_KEEP must appear in the
    returned profile.  Noisy fields (phone, irrelevantField, …) must be
    stripped so the LLM receives a focused context.
    """
    result = _process_company_profile(VALID_COMPANY_RAW)

    assert result["ok"] is True
    assert result["ticker"] == "NVDA"

    profile = result["profile"]
    allowed = {
        "name", "country", "currency", "exchange",
        "finnhubIndustry", "ipo", "marketCapitalization",
        "shareOutstanding", "weburl",
    }
    assert set(profile.keys()) <= allowed, (
        f"Unexpected keys in profile: {set(profile.keys()) - allowed}"
    )
    # Spot-check that known-good fields survived
    assert profile["name"] == "NVIDIA Corp"
    assert profile["finnhubIndustry"] == "Semiconductors"

    # Confirm noisy fields were stripped
    assert "irrelevantField" not in profile
    assert "phone" not in profile


# ===========================================================================
# 3. Tool-level smoke tests — wiring to API clients
# ===========================================================================


def test_get_income_statement_annual_tool_returns_error_on_api_failure():
    """
    When the underlying AlphaVantage client returns ok=False, the tool
    must propagate a well-formed error dict (not raise, not return raw).

    Patches avclient at the module level so no HTTP call is made.
    """
    error_raw = {"ok": False, "ticker": "FAKE", "error": "premium endpoint"}

    with patch.object(
        tools_module.avclient,
        "get_income_statement_annual",
        return_value=error_raw,
    ):
        result = tools_module.get_income_statement_annual.invoke({"ticker": "FAKE"})

    assert result["ok"] is False
    assert "instruction" in result


def test_get_income_statement_annual_tool_returns_processed_data_on_success():
    """
    When the client returns a valid response the tool must pass it through
    _process_income_statement and return a structured result.

    Patches avclient at the module level so no HTTP call is made.
    """
    with patch.object(
        tools_module.avclient,
        "get_income_statement_annual",
        return_value=VALID_INCOME_RAW,
    ):
        result = tools_module.get_income_statement_annual.invoke({"ticker": "NVDA"})

    assert result["ok"] is True
    assert result["ticker"] == "NVDA"
    assert result["currency_unit"] == "USD_billions"
    assert len(result["statements"]) > 0


def test_get_company_profile_tool_raises_on_api_failure():
    """
    When FinnHub returns ok=False the tool must raise ValueError (via
    _process_company_profile), signalling a hard failure to the agent.

    Patches finnclient at the module level so no HTTP call is made.
    """
    error_raw = {"ok": False, "ticker": "FAKE", "error": "unknown symbol"}

    with patch.object(
        tools_module.finnclient,
        "company_profile2",
        return_value=error_raw,
    ):
        with pytest.raises(ValueError, match="FAKE"):
            tools_module.get_company_profile.invoke({"ticker": "FAKE"})


def test_get_company_profile_tool_returns_filtered_profile_on_success():
    """
    When FinnHub returns a valid profile the tool must strip noisy fields
    and return only the allowed subset.

    Patches finnclient at the module level so no HTTP call is made.
    """
    with patch.object(
        tools_module.finnclient,
        "company_profile2",
        return_value=VALID_COMPANY_RAW,
    ):
        result = tools_module.get_company_profile.invoke({"ticker": "NVDA"})

    assert result["ok"] is True
    assert "irrelevantField" not in result["profile"]
    assert "name" in result["profile"]
