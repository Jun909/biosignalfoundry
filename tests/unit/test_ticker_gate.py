"""
Tests for src/core/ticker_gate.py.

Name→ticker resolution runs against the real company table bundled with
edgartools (offline, no network), so these tests also catch a data/format
change on an edgartools upgrade. Finnhub is the only thing mocked: `_finnhub`
is patched with a fake whose profiles come from a dict.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.core import ticker_gate
from src.core.ticker_gate import (
    GateUnavailable,
    TickerRejected,
    normalize_name,
    resolve_biotech_ticker,
)


def profile(industry, name="X"):
    return {"ok": True, "data": {"finnhubIndustry": industry, "name": name}}


def fake_finnhub(profiles: dict):
    """profiles: ticker -> response dict (anything missing is an empty profile)."""
    client = MagicMock()
    client.company_profile2.side_effect = lambda ticker: profiles.get(
        ticker, {"ok": True, "data": {}}
    )
    return client


def use_profiles(profiles: dict):
    return patch.object(ticker_gate, "_finnhub", return_value=fake_finnhub(profiles))


# ---------------------------------------------------------------------------
# normalize_name
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Moderna, Inc.", "moderna"),
        ("MODERNA", "moderna"),
        ("moderna stock", "moderna"),
        ("ELI LILLY & Co", "eli lilly"),
        ("Eli Lilly and Company", "eli lilly"),
        ("VERTEX PHARMACEUTICALS INC / MA", "vertex pharmaceuticals"),
        ("CRISPR Therapeutics AG", "crispr therapeutics"),
    ],
)
def test_normalize_name(raw, expected):
    assert normalize_name(raw) == expected


# ---------------------------------------------------------------------------
# Resolution: tickers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text", ["MRNA", "mrna", "$MRNA", "  MRNA  "])
async def test_ticker_forms_resolve(text):
    with use_profiles({"MRNA": profile("Biotechnology", "Moderna, Inc.")}):
        resolved = await resolve_biotech_ticker(text)

    assert resolved.ticker == "MRNA"
    assert resolved.industry == "Biotechnology"


async def test_ticker_lookup_makes_a_single_finnhub_call():
    fake = fake_finnhub({"MRNA": profile("Biotechnology")})
    with patch.object(ticker_gate, "_finnhub", return_value=fake):
        await resolve_biotech_ticker("MRNA")

    fake.company_profile2.assert_called_once_with(ticker="MRNA")


# ---------------------------------------------------------------------------
# Resolution: company names
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text, ticker",
    [
        ("Moderna", "MRNA"),
        ("moderna stock", "MRNA"),
        ("Moderna Inc", "MRNA"),
        ("Regeneron", "REGN"),
        ("Eli Lilly and Co", "LLY"),
        ("CRISPR Therapeutics", "CRSP"),
    ],
)
async def test_company_names_resolve(text, ticker):
    with use_profiles({ticker: profile("Biotechnology")}):
        resolved = await resolve_biotech_ticker(text)

    assert resolved.ticker == ticker


async def test_pharmaceuticals_industry_is_accepted():
    with use_profiles({"LLY": profile("Pharmaceuticals", "Eli Lilly and Company")}):
        resolved = await resolve_biotech_ticker("Eli Lilly")

    assert resolved.ticker == "LLY"
    assert resolved.industry == "Pharmaceuticals"


async def test_ambiguous_name_is_resolved_by_sector():
    """ "Vertex" matches Vertex Pharmaceuticals (VRTX) and Vertex, Inc. (VERX,
    software). The sector check picks the biotech one."""
    with use_profiles(
        {"VRTX": profile("Biotechnology"), "VERX": profile("Technology")}
    ):
        resolved = await resolve_biotech_ticker("Vertex")

    assert resolved.ticker == "VRTX"


async def test_several_biotech_matches_are_rejected_as_ambiguous():
    fake_candidates = [
        ticker_gate._Company("AAA", "Alpha Bio", "alpha bio"),
        ticker_gate._Company("BBB", "Alpha Bio II", "alpha bio ii"),
    ]
    with (
        patch.object(ticker_gate, "_candidates", return_value=fake_candidates),
        use_profiles(
            {"AAA": profile("Biotechnology"), "BBB": profile("Biotechnology")}
        ),
    ):
        with pytest.raises(TickerRejected, match="AAA, BBB"):
            await resolve_biotech_ticker("alpha bio")


# ---------------------------------------------------------------------------
# Rejections
# ---------------------------------------------------------------------------


async def test_non_biotech_company_is_rejected_with_its_industry():
    with use_profiles({"AAPL": profile("Technology", "Apple Inc.")}):
        with pytest.raises(TickerRejected, match="Technology"):
            await resolve_biotech_ticker("AAPL")


async def test_unknown_company_is_rejected():
    with use_profiles({}):
        with pytest.raises(TickerRejected, match="Couldn't find"):
            await resolve_biotech_ticker("Zzyzx Qwertyland")


async def test_unknown_company_makes_no_finnhub_call():
    fake = fake_finnhub({})
    with patch.object(ticker_gate, "_finnhub", return_value=fake):
        with pytest.raises(TickerRejected):
            await resolve_biotech_ticker("Zzyzx Qwertyland")

    fake.company_profile2.assert_not_called()


@pytest.mark.parametrize("text", ["", "  ", "$", "q1", "x!"])
async def test_too_short_or_empty_input_is_rejected(text):
    with use_profiles({}):
        with pytest.raises(TickerRejected, match="company name or stock ticker"):
            await resolve_biotech_ticker(text)


async def test_sentence_is_rejected_not_guessed():
    with use_profiles({}):
        with pytest.raises(TickerRejected):
            await resolve_biotech_ticker("check if i should buy moderna stocks")


async def test_real_tickers_win_over_short_names():
    """ "BIO" is Bio-Rad's ticker, so it resolves as a ticker, not as the word."""
    with use_profiles({"BIO": profile("Life Sciences Tools & Services")}):
        with pytest.raises(TickerRejected, match="BIO"):
            await resolve_biotech_ticker("bio")


async def test_overly_broad_name_is_rejected_as_too_many_matches():
    with use_profiles({}):
        with pytest.raises(TickerRejected, match="too many companies"):
            await resolve_biotech_ticker("american")


async def test_ticker_with_empty_profile_is_rejected():
    with use_profiles({"MRNA": {"ok": True, "data": {}}}):
        with pytest.raises(TickerRejected, match="No company profile"):
            await resolve_biotech_ticker("MRNA")


def test_otc_and_unlisted_rows_are_excluded_from_the_table():
    df = pd.DataFrame(
        {
            "cik": [1, 2, 3],
            "ticker": ["LIST", "OTCX", "NONE"],
            "exchange": ["Nasdaq", "OTC", None],
            "company": ["Listed Bio Inc", "Otc Bio Inc", "Unknown Bio Inc"],
        }
    )
    ticker_gate._companies.cache_clear()
    try:
        with patch.object(
            ticker_gate, "load_company_tickers_from_package", return_value=df
        ):
            assert [c.ticker for c in ticker_gate._companies()] == ["LIST"]
    finally:
        ticker_gate._companies.cache_clear()


# ---------------------------------------------------------------------------
# Finnhub failures fail closed
# ---------------------------------------------------------------------------


async def test_finnhub_error_raises_gate_unavailable():
    with use_profiles({"MRNA": {"ok": False, "error": "429 Too Many Requests"}}):
        with pytest.raises(GateUnavailable):
            await resolve_biotech_ticker("MRNA")


async def test_finnhub_error_on_any_candidate_raises_gate_unavailable():
    with use_profiles(
        {"VRTX": profile("Biotechnology"), "VERX": {"ok": False, "error": "boom"}}
    ):
        with pytest.raises(GateUnavailable):
            await resolve_biotech_ticker("Vertex")
