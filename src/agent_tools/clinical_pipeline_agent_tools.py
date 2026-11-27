import re
import time
from functools import lru_cache

import structlog
from langchain.tools import tool

from config import FINNHUB_API_KEY, OPENFDA_API_KEY, SEC_EDGAR_IDENTITY
from src.data_providers.finnhub import FinnHubAPIClient
from src.data_providers.openfda import (
    Dataset,
    OpenFDAAPIClient,
    Query,
    SearchClause,
    company_search_keys,
    matches_company,
)
from src.data_providers.sec_edgar import SECEdgarClient

logger = structlog.get_logger()

finnclient = FinnHubAPIClient(api_key=FINNHUB_API_KEY or "")
fdaclient = OpenFDAAPIClient(api_key=OPENFDA_API_KEY or "")

MAX_APPLICATIONS = 15
MAX_LETTERS = 5
LETTER_EXCERPT_CHARS = 800
MAX_8K_FILINGS = 8
FILINGS_TO_SCAN = 20
PRESS_RELEASE_EXCERPT_CHARS = 1200
ITEM_EXCERPT_CHARS = 800

# 8-K items that can carry clinical or regulatory news. Left out on purpose:
# 5.02 (officer changes), 5.03, 5.07 (votes), 2.03, 3.02 (financing), 9.01 (exhibit list).
RELEVANT_8K_ITEMS = {"1.01", "1.02", "2.02", "2.05", "2.06", "3.01", "7.01", "8.01"}

NOT_RETRY = "Data is unavailable from the provider. Do not retry this tool call."

BIOLOGICS_NOTE = (
    "drug/drugsfda covers NDAs and ANDAs only. Biologics (vaccines, antibodies and "
    "other BLA products) are not in this dataset, so an empty result does NOT mean "
    "the company has no approvals."
)


@lru_cache(maxsize=1)
def _sec_client() -> SECEdgarClient:
    if not SEC_EDGAR_IDENTITY:
        raise RuntimeError("SEC_EDGAR_IDENTITY is not set")
    return SECEdgarClient(identity_email=SEC_EDGAR_IDENTITY)


def _error(ticker: str, error: str | None) -> dict:
    return {
        "ok": False,
        "ticker": ticker,
        "error": error or "Unknown error",
        "instruction": NOT_RETRY,
    }


def _resolve_company_name(ticker: str) -> tuple[str | None, str | None]:
    """Listed company name from Finnhub (cached), or (None, reason)."""
    profile = finnclient.company_profile2(ticker=ticker)
    if not profile.get("ok"):
        return None, f"Company profile lookup failed: {profile.get('error')}"
    name = (profile.get("data") or {}).get("name")
    if not name:
        return None, "No company profile found for this ticker"
    return name, None


def _date_key(yyyymmdd: str | None) -> str:
    return yyyymmdd or ""


def _fmt_date(yyyymmdd: str | None) -> str | None:
    if yyyymmdd and len(yyyymmdd) == 8:
        return f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:]}"
    return yyyymmdd


def _summarize_application(app: dict) -> dict:
    products = app.get("products") or []
    submissions = app.get("submissions") or []

    originals = [
        s
        for s in submissions
        if s.get("submission_type") == "ORIG" and s.get("submission_status") == "AP"
    ]
    original = min(
        originals,
        key=lambda s: _date_key(s.get("submission_status_date")),
        default=None,
    )
    latest = max(
        submissions,
        key=lambda s: _date_key(s.get("submission_status_date")),
        default=None,
    )

    brands = sorted({p["brand_name"] for p in products if p.get("brand_name")})
    ingredients = sorted(
        {
            ai["name"]
            for p in products
            for ai in p.get("active_ingredients") or []
            if ai.get("name")
        }
    )
    statuses = sorted(
        {p["marketing_status"] for p in products if p.get("marketing_status")}
    )

    summary = {
        "application_number": app.get("application_number"),
        "sponsor": app.get("sponsor_name"),
        "brand_names": brands,
        "active_ingredients": ingredients,
        "marketing_status": statuses,
        "original_approval_date": _fmt_date(
            original.get("submission_status_date") if original else None
        ),
        "review_priority": original.get("review_priority") if original else None,
        "supplements": sum(
            1 for s in submissions if s.get("submission_type") == "SUPPL"
        ),
    }
    if latest:
        summary["latest_submission"] = {
            "type": latest.get("submission_type"),
            "status": latest.get("submission_status"),
            "date": _fmt_date(latest.get("submission_status_date")),
            "class": latest.get("submission_class_code_description"),
        }
    return summary


def _process_fda_approvals(
    ticker: str, company: str, applications: list[dict], truncated: bool
) -> dict:
    summaries = [_summarize_application(a) for a in applications]
    summaries.sort(key=lambda a: a["original_approval_date"] or "", reverse=True)
    omitted = max(0, len(summaries) - MAX_APPLICATIONS)
    result = {
        "ok": True,
        "ticker": ticker,
        "company": company,
        "matched_sponsors": sorted({a["sponsor"] for a in summaries if a["sponsor"]}),
        "application_count": len(summaries),
        "applications": summaries[:MAX_APPLICATIONS],
        "note": BIOLOGICS_NOTE,
    }
    if omitted:
        result["applications_omitted"] = omitted
    if truncated:
        result["warning"] = "The provider result was truncated; the list is incomplete."
    if not summaries:
        result["message"] = f"No NDA/ANDA applications found for sponsor '{company}'."
    return result


_REASON_START = re.compile(
    r"(cannot approve|can not approve|not approvable|deficienc|refuse to file|"
    r"we have completed our review)",
    re.IGNORECASE,
)


def _letter_excerpt(text: str | None) -> str:
    """The part of a letter that states why it was issued. The text is OCR output with
    redaction artifacts, so start near the decision sentence rather than the letterhead.
    """
    clean = re.sub(r"\s+", " ", text or "").strip()
    match = _REASON_START.search(clean)
    start = match.start() if match else 0
    excerpt = clean[start : start + LETTER_EXCERPT_CHARS]
    return excerpt + ("..." if start + LETTER_EXCERPT_CHARS < len(clean) else "")


def _process_crl(ticker: str, company: str, letters: list[dict]) -> dict:
    ordered = sorted(
        letters, key=lambda x: _crl_sort_key(x.get("letter_date")), reverse=True
    )
    result = {
        "ok": True,
        "ticker": ticker,
        "company": company,
        "letter_count": len(ordered),
        "letters": [
            {
                "letter_date": x.get("letter_date"),
                "letter_type": x.get("letter_type"),
                "application_number": x.get("application_number"),
                "approval_status": x.get("approval_status"),
                "company_name": x.get("company_name"),
                "excerpt": _letter_excerpt(x.get("text")),
            }
            for x in ordered[:MAX_LETTERS]
        ],
        "note": (
            "Published FDA complete response letters (a CRL means the FDA declined to "
            "approve the application as submitted). approval_status is the dataset's "
            "flag for the application: 'Approved' means it is approved, 'Unapproved' "
            "means it is not. The dataset only holds letters FDA has published, so an "
            "empty result does not prove the company never received one."
        ),
    }
    if len(ordered) > MAX_LETTERS:
        result["letters_omitted"] = len(ordered) - MAX_LETTERS
    if not ordered:
        result["message"] = (
            f"No published complete response letters found for '{company}'."
        )
    return result


def _crl_sort_key(letter_date: str | None) -> str:
    # letter_date is MM/DD/YYYY; sort chronologically
    try:
        month, day, year = (letter_date or "").split("/")
        return f"{year}{month}{day}"
    except ValueError:
        return ""


def _clip(text: str | None, limit: int) -> str:
    clean = re.sub(r"\s+", " ", text or "").strip()
    return clean if len(clean) <= limit else clean[:limit] + "..."


def _process_8k(ticker: str, filings: list[dict]) -> dict:
    events = []
    for filing in filings:
        relevant = [
            i for i in filing.get("items_reported") or [] if i in RELEVANT_8K_ITEMS
        ]
        if not relevant:
            continue
        details = {d["item_id"]: d for d in filing.get("details") or []}
        event = {
            "filing_date": (filing.get("filing_date") or "")[:10],
            "items": [
                {
                    "item": i,
                    "name": (details.get(i) or {}).get("display_name"),
                    "title": (details.get(i) or {}).get("title"),
                }
                for i in relevant
            ],
            "url": filing.get("url"),
        }
        press_release = filing.get("press_release")
        if press_release:
            event["press_release_excerpt"] = _clip(
                press_release, PRESS_RELEASE_EXCERPT_CHARS
            )
        else:
            # No exhibit: the announcement is in the filing body itself.
            seen, parts = set(), []
            for i in relevant:
                content = (details.get(i) or {}).get("content")
                if content and content not in seen:
                    seen.add(content)
                    parts.append(_clip(content, ITEM_EXCERPT_CHARS))
            if parts:
                event["text_excerpt"] = " | ".join(parts)
        events.append(event)

    events = events[:MAX_8K_FILINGS]
    result = {
        "ok": True,
        "ticker": ticker,
        "filings_scanned": len(filings),
        "event_count": len(events),
        "events": events,
        "note": (
            "Recent 8-K current reports with items that can carry clinical or "
            "regulatory news (1.01, 1.02, 2.02, 2.05, 2.06, 3.01, 7.01, 8.01). Item 3.01 "
            "is a listing-standard (e.g. Nasdaq delisting) notice. Financing, officer "
            "and shareholder-vote items are left out."
        ),
    }
    if not filings:
        result["message"] = (
            "No 8-K filings found. Foreign private issuers file 6-K/20-F instead, "
            "which this tool does not cover."
        )
    elif not events:
        result["message"] = (
            "None of the recent 8-Ks report clinical or regulatory items."
        )
    return result


@tool
def get_fda_approvals(ticker: str) -> dict:
    """
    Provides a biotech company's FDA drug approval history (NDAs and ANDAs): one entry
    per application with brand names, active ingredients, the original approval date,
    review priority and the latest submission. Does NOT cover biologics (vaccines,
    antibodies), so an empty result does not mean the company has no approvals.
    Args:
        ticker: The ticker of a company. Example: VRTX for Vertex Pharmaceuticals
    """
    ticker = ticker.strip().upper()
    start = time.perf_counter()
    company, problem = _resolve_company_name(ticker)
    if not company:
        return _error(ticker, problem)

    applications: list[dict] = []
    truncated = False
    error = None
    for key in company_search_keys(company):
        raw = fdaclient.query_all(
            Dataset.DRUG_FDA, Query(search=[SearchClause("sponsor_name", f"{key}*")])
        )
        if not raw.get("ok"):
            error = raw.get("error")
            break
        applications = [
            a
            for a in raw["data"].get("results", [])
            if matches_company(company, a.get("sponsor_name"))
        ]
        truncated = bool(raw.get("truncated"))
        if applications:
            break

    result = (
        _error(ticker, error)
        if error
        else _process_fda_approvals(ticker, company, applications, truncated)
    )
    logger.info(
        "api_call",
        tool="get_fda_approvals",
        provider="openfda",
        ticker=ticker,
        duration_ms=round((time.perf_counter() - start) * 1000),
        ok=result.get("ok"),
        applications=result.get("application_count"),
        error=result.get("error"),
    )
    return result


@tool
def get_fda_complete_response_letters(ticker: str) -> dict:
    """
    Provides the FDA complete response letters (rejections of a drug application as
    submitted) published for a biotech company, newest first, with the application
    number, whether that application is now approved, and an excerpt stating the
    FDA's reasons. Only letters the FDA has published are included.
    Args:
        ticker: The ticker of a company. Example: ALDX for Aldeyra Therapeutics
    """
    ticker = ticker.strip().upper()
    start = time.perf_counter()
    company, problem = _resolve_company_name(ticker)
    if not company:
        return _error(ticker, problem)

    letters: list[dict] = []
    error = None
    for key in company_search_keys(company):
        raw = fdaclient.query_all(
            Dataset.TRANSPARENCY,
            Query(search=[SearchClause("company_name", key)]),
        )
        if not raw.get("ok"):
            error = raw.get("error")
            break
        letters = [
            x
            for x in raw["data"].get("results", [])
            if matches_company(company, x.get("company_name"))
        ]
        if letters:
            break

    result = _error(ticker, error) if error else _process_crl(ticker, company, letters)
    logger.info(
        "api_call",
        tool="get_fda_complete_response_letters",
        provider="openfda",
        ticker=ticker,
        duration_ms=round((time.perf_counter() - start) * 1000),
        ok=result.get("ok"),
        letters=result.get("letter_count"),
        error=result.get("error"),
    )
    return result


@tool
def get_recent_8k_events(ticker: str) -> dict:
    """
    Provides recent SEC 8-K current reports of a US-listed company that can carry
    clinical or regulatory news (trial results, FDA interactions, material agreements,
    earnings business updates, listing-standard notices), newest first, each with the
    filing date, the items reported, a link, and an excerpt of the press release or
    filing text. Foreign filers (6-K/20-F) are not covered.
    Args:
        ticker: The ticker of a company. Example: MRNA for Moderna
    """
    ticker = ticker.strip().upper()
    start = time.perf_counter()
    try:
        raw = _sec_client().get_8k_data(ticker, limit=FILINGS_TO_SCAN)
    except Exception as e:  # missing identity, edgartools failure
        raw = {"ok": False, "error": str(e)}
    result = (
        _process_8k(ticker, raw.get("data") or [])
        if raw.get("ok")
        else _error(ticker, raw.get("error"))
    )
    logger.info(
        "api_call",
        tool="get_recent_8k_events",
        provider="sec_edgar",
        ticker=ticker,
        duration_ms=round((time.perf_counter() - start) * 1000),
        ok=result.get("ok"),
        events=result.get("event_count"),
        error=result.get("error"),
    )
    return result
