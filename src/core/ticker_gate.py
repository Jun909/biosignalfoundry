"""
Deterministic ticker resolution + biotech sector gate.

Turns a user's company name or ticker into one validated biotech ticker before
any paid LLM call. No LLM is involved.

1. Resolve: a ticker-shaped input is looked up directly; otherwise the text is
   matched against the SEC company list bundled with edgartools (offline, no
   API quota).
2. Gate: each candidate's Finnhub ``finnhubIndustry`` must be in
   ``BIOTECH_INDUSTRIES``. Because the sector check runs on every candidate, a
   name that matches several companies ("Vertex") resolves to the biotech one.

Failures split into two exceptions the caller maps to different responses:
``TickerRejected`` (bad input, safe to show the user) and ``GateUnavailable``
(Finnhub failed; retry later, never cached as an answer).
"""

import asyncio
import re
from dataclasses import dataclass
from functools import lru_cache

import structlog
from edgar.reference.tickers import load_company_tickers_from_package

from config import settings
from src.data_providers.finnhub import FinnHubAPIClient

logger = structlog.get_logger()

# Finnhub labels observed for the watchlist: "Biotechnology" for the pure
# biotechs, "Pharmaceuticals" for large pharma such as Eli Lilly.
BIOTECH_INDUSTRIES = frozenset({"Biotechnology", "Pharmaceuticals"})

# OTC listings are excluded: thin, often foreign, and they inflate name
# collisions. Widen this set if OTC biotechs should be analysable.
ALLOWED_EXCHANGES = frozenset({"Nasdaq", "NYSE", "CBOE"})

MIN_NAME_LENGTH = 3
MAX_CANDIDATES = 5

_TICKER_RE = re.compile(r"^\$?([A-Za-z]{1,5}(?:[.-][A-Za-z])?)$")
_STATE_SUFFIX_RE = re.compile(r"\s*/\s*[a-z]{2,3}\s*/?\s*$")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9 ]+")
_FILLER_WORDS = frozenset(
    {
        "inc", "incorporated", "corp", "corporation", "co", "company", "ltd",
        "limited", "plc", "ag", "sa", "nv", "llc", "lp", "the", "stock",
        "stocks", "shares", "share",
    }
)  # fmt: skip


class TickerRejected(Exception):
    """The input can't be analysed. The message is safe to show the user."""


class GateUnavailable(Exception):
    """Finnhub failed, so the sector check couldn't run. Retry later."""


@dataclass(frozen=True)
class ResolvedTicker:
    ticker: str
    company_name: str
    industry: str


@dataclass(frozen=True)
class _Company:
    ticker: str
    name: str
    normalized: str


def normalize_name(text: str) -> str:
    """Lowercase, drop punctuation, legal suffixes and filler ("Inc", "stock")."""
    text = text.lower().replace("&", " and ")
    text = _STATE_SUFFIX_RE.sub("", text)
    text = _NON_ALNUM_RE.sub(" ", text)
    words = [w for w in text.split() if w not in _FILLER_WORDS]
    while words and words[-1] == "and":
        words.pop()
    return " ".join(words)


@lru_cache(maxsize=1)
def _companies() -> tuple[_Company, ...]:
    df = load_company_tickers_from_package()
    if df is None:
        raise RuntimeError("edgartools bundled company ticker data is unavailable")
    df = df[df["exchange"].isin(ALLOWED_EXCHANGES)]
    return tuple(
        _Company(
            ticker=row.ticker, name=row.company, normalized=normalize_name(row.company)
        )
        for row in df.itertuples()
    )


@lru_cache(maxsize=1)
def _by_ticker() -> dict[str, _Company]:
    return {c.ticker: c for c in _companies()}


@lru_cache(maxsize=1)
def _finnhub() -> FinnHubAPIClient:
    return FinnHubAPIClient(api_key=settings.finnhub_api_key)


def _candidates(user_input: str) -> list[_Company]:
    """Companies the input could refer to, best (exact name) matches first."""
    stripped = user_input.strip()

    ticker_match = _TICKER_RE.match(stripped)
    if ticker_match:
        company = _by_ticker().get(ticker_match.group(1).upper().replace(".", "-"))
        if company:
            return [company]

    query = normalize_name(stripped)
    if len(query) < MIN_NAME_LENGTH:
        raise TickerRejected(
            "Enter a biotech company name or stock ticker, e.g. Moderna or MRNA."
        )

    exact = [c for c in _companies() if c.normalized == query]
    prefix = [c for c in _companies() if c.normalized.startswith(query + " ")]
    found = exact + prefix
    if not found:
        raise TickerRejected(
            f"Couldn't find a listed company matching '{stripped}'. "
            "Try its stock ticker instead."
        )
    if len(found) > MAX_CANDIDATES:
        raise TickerRejected(
            f"'{stripped}' matches too many companies. "
            "Enter the full company name or its stock ticker."
        )
    return found


def _industry(company: _Company) -> str | None:
    """Finnhub industry for a company; None if Finnhub has no profile for it."""
    result = _finnhub().company_profile2(ticker=company.ticker)
    if not result.get("ok"):
        logger.warning(
            "finnhub profile lookup failed",
            ticker=company.ticker,
            error=result.get("error"),
        )
        raise GateUnavailable(f"Finnhub profile lookup failed for {company.ticker}")
    profile = result.get("data") or {}
    return profile.get("finnhubIndustry") or None


async def resolve_biotech_ticker(user_input: str) -> ResolvedTicker:
    """Resolve ``user_input`` to exactly one biotech ticker or raise.

    Raises:
        TickerRejected: unresolvable, ambiguous, or not a biotech company.
        GateUnavailable: Finnhub failed; the user should retry shortly.
    """
    candidates = _candidates(user_input)

    # Blocking SDK calls (and the client's throttle sleep) stay off the event loop.
    industries = await asyncio.gather(
        *(asyncio.to_thread(_industry, c) for c in candidates)
    )

    matches = [
        ResolvedTicker(ticker=c.ticker, company_name=c.name, industry=ind)
        for c, ind in zip(candidates, industries)
        if ind in BIOTECH_INDUSTRIES
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        tickers = ", ".join(m.ticker for m in matches)
        raise TickerRejected(
            f"'{user_input.strip()}' matches several biotech tickers ({tickers}). "
            "Enter the one you want."
        )

    first, first_industry = candidates[0], industries[0]
    if first_industry:
        raise TickerRejected(
            f"{first.name} ({first.ticker}) is classified as '{first_industry}', "
            "not biotech or pharma."
        )
    raise TickerRejected(
        f"No company profile is available for '{user_input.strip()}', "
        "so it can't be verified as a biotech company."
    )
