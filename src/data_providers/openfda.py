import hashlib
import re
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any
from urllib.parse import quote, urlencode

import requests

from config import REDIS_CACHE_TTL_SECONDS_OPENFDA
from src.data_providers.cache import cached_call


class Dataset(str, Enum):
    ANIMAL_AND_VETERINARY_EVENT = "animalandveterinary/event"
    DRUG_EVENT = "drug/event"
    DRUG_LABEL = "drug/label"
    DRUG_NDC = "drug/ndc"
    DRUG_ENFORCEMENT = "drug/enforcement"
    DRUG_FDA = "drug/drugsfda"
    DRUG_SHORTAGE = "drug/shortages"
    DEVICE_501K = "device/510k"
    DEVICE_CLASSIFICATION = "device/classification"
    DEVICE_ENFORCEMENT = "device/enforcement"
    DEVICE_EVENT = "device/event"
    DEVICE_PREMARKET_APPROVAL = "device/pma"
    DEVICE_RECALL = "device/recall"
    DEVICE_REGISTRATION_LISTING = "device/registrationlisting"
    DEVICE_COVID19_SEROLOGY = "device/covid19serology"
    DEVICE_UNIQUE_DEVICE_IDENTIFIER = "device/udi"
    FOOD_ENFORCEMENT = "food/enforcement"
    FOOD_EVENT = "food/event"
    COSMETIC_EVENT = "cosmetic/event"
    HISTORICAL_DOCUMENT = "other/historicaldocument"
    NSDE = "other/nsde"
    SUBSTANCE_DATA_REPORTS = "other/substance"
    UNII = "other/unii"
    TOBACCO_PROBLEM = "tobacco/problem"
    TRANSPARENCY = "transparency/crl"


def _alnum_tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[^A-Za-z0-9]+", text.upper()) if t]


def company_search_keys(company_name: str) -> list[str]:
    """Search terms to find a company in OpenFDA from its listed name, best first.

    Sponsor and company fields are spelled inconsistently ("Intra-Cellular" vs
    "INTRACELLULAR"), so this returns the first word with punctuation removed
    ("INTRACELLULAR") and the first alphanumeric token ("INTRA"). Search with each in
    turn and filter the hits with ``matches_company``.
    """
    words = company_name.split()
    if not words:
        return []
    keys = ["".join(_alnum_tokens(words[0]))]
    tokens = _alnum_tokens(company_name)
    if tokens and tokens[0] not in keys:
        keys.append(tokens[0])
    return [k for k in keys if k]


def matches_company(company_name: str, sponsor: str) -> bool:
    """True if ``sponsor`` starts with the company's first word as whole word(s).

    "BIOGEN IDEC INC" and "INTRA-CELLULAR" match "Biogen Inc." and "Intra-Cellular
    Therapies Inc"; "BIOGENERIX" and "INTRABIO" do not.
    """
    words = company_name.split()
    if not words or not sponsor:
        return False
    target = "".join(_alnum_tokens(words[0]))
    joined = ""
    for token in _alnum_tokens(sponsor):
        joined += token
        if joined == target:
            return True
        if len(joined) >= len(target):
            return False
    return False


class SearchClause:
    def __init__(self, field: str, term: str):
        self.field = field
        self.term = term

    def to_query(self) -> str:
        return f"{self.field}:{self.term}"


class Query:
    def __init__(
        self,
        search: list[SearchClause] | None = None,
        operator: str = "AND",
        sort: str | None = None,
        count: str | None = None,
        limit: int = 100,
        skip: int = 0,
        date_filter: bool = False,
    ):
        """
        Args:
            search: What to search for
            operator: "AND" or "+".
            sort: Sort the search result. eg "{field}:asc". Works only if field exists in the dataset.
            count: Count the number of unique values. eg "patient.reaction.reactionmeddrapt.exact"
            limit: Return up to this number of records that matches the search parameter
            skip: Skip this number of records that matches the search parameter
            date_filter: Set to "True" when the 'term' is a date range, eg [20180101+TO+20200723]
        """
        self.search = search or []
        self.operator = operator
        self.sort = sort
        self.count = count
        self.limit = limit
        self.skip = skip
        self.date_filter = date_filter

    def compile(self) -> tuple[dict[str, str], bool]:
        params: dict[str, str] = {}

        if self.search:
            if self.operator == "AND":
                sep = "+AND+"
            elif self.operator == "+":
                sep = "+"
            else:
                raise ValueError(f"Unsupported operator: {self.operator}")
            params["search"] = sep.join(clause.to_query() for clause in self.search)

        if self.count:
            params["count"] = self.count
        else:
            params["limit"] = str(self.limit)
            params["skip"] = str(self.skip)

        if self.sort:
            params["sort"] = self.sort

        return params, self.date_filter


class OpenFDAAPIClient:
    BASE_URL = "https://api.fda.gov"
    # openFDA allows at most 1000 records per request and skip <= 25000.
    MAX_PAGE = 1000
    MAX_SKIP = 25000

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.provider = "OpenFDA"

    def _wrap_response(self, data: Any, endpoint: str, skip: int = 0) -> dict:
        payload = {
            "provider": self.provider,
            "endpoint": endpoint,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
            "ok": True,
        }
        # Surface truncation: a result list shorter than the match count must not
        # look like the complete answer.
        total = ((data or {}).get("meta") or {}).get("results", {}).get("total")
        if total is not None:
            returned = len((data or {}).get("results") or [])
            payload["total"] = total
            payload["truncated"] = skip + returned < total
        return payload

    def _error(self, e: Exception | str, endpoint: str) -> dict:
        return {
            "provider": self.provider,
            "endpoint": endpoint,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": [],
            "ok": False,
            "error": self._redact(str(e)),
        }

    def _redact(self, text: str) -> str:
        """requests puts the full URL, including api_key, in its error messages."""
        if self.api_key:
            text = text.replace(self.api_key, "***")
        return text

    def query(self, dataset: Dataset, query: Query) -> dict:
        """Run a query (cached in Redis for a day when successful).

        ``ok`` is False only for real failures: a query that matches nothing (HTTP
        404 "No matches found!") returns ``ok=True`` with empty results. When the
        match count exceeds what was returned, ``truncated`` is True; use
        ``query_all`` to page through.
        """
        endpoint = dataset.value
        params, _ = query.compile()
        # Build the query string by hand: terms use "+" for spaces and as the AND
        # separator, and ":*[]\"" are meaningful to OpenFDA. requests would encode
        # "+" as %2B and the API would answer 500.
        qs = urlencode(params, quote_via=quote, safe=':+*[]"')
        digest = hashlib.sha256(qs.encode()).hexdigest()[:24]
        return cached_call(
            f"openfda:{endpoint}:{digest}",
            REDIS_CACHE_TTL_SECONDS_OPENFDA,
            lambda: self._fetch(endpoint, qs, query.skip),
        )

    def _fetch(self, endpoint: str, qs: str, skip: int) -> dict:
        if self.api_key:
            qs = f"{qs}&api_key={self.api_key}"
        url = f"{self.BASE_URL}/{endpoint}.json?{qs}"

        try:
            response = requests.get(url, timeout=self.timeout)
        except requests.RequestException as e:
            return self._error(e, endpoint)

        if response.status_code == 404:
            return self._wrap_response({"meta": {}, "results": []}, endpoint)

        try:
            response.raise_for_status()
            return self._wrap_response(response.json(), endpoint, skip)
        except Exception as e:
            detail = ""
            try:
                detail = response.json().get("error", {}).get("message", "")
            except ValueError:
                pass
            return self._error(f"{e} {detail}".strip(), endpoint)

    def query_all(
        self, dataset: Dataset, query: Query, max_records: int = 1000
    ) -> dict:
        """Page through every match, up to ``max_records``.

        Returns one response with the merged ``results``. ``truncated`` is True if
        matches remain beyond ``max_records`` (or openFDA's skip limit).
        """
        if query.count:
            raise ValueError("query_all does not support count queries")
        page = min(self.MAX_PAGE, max_records)
        merged: list = []
        first: dict | None = None
        total: int | None = None
        skip = query.skip
        while len(merged) < max_records and skip <= self.MAX_SKIP:
            page_query = Query(
                search=query.search,
                operator=query.operator,
                sort=query.sort,
                limit=min(page, max_records - len(merged)),
                skip=skip,
            )
            resp = self.query(dataset, page_query)
            if not resp["ok"]:
                return resp
            first = first or resp
            results = resp["data"].get("results") or []
            merged.extend(results)
            total = resp.get("total", total)
            skip += len(results)
            if not results or (total is not None and skip >= total):
                break
        assert first is not None
        data = {"meta": first["data"].get("meta", {}), "results": merged}
        out = dict(first)
        out["data"] = data
        out["truncated"] = total is not None and (query.skip + len(merged)) < total
        if total is not None:
            out["total"] = total
        return out
