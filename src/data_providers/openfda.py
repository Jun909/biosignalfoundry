from datetime import date, datetime, timezone
from enum import Enum
from typing import Any
from urllib.parse import quote, urlencode

import requests


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

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.provider = "OpenFDA"

    def _wrap_response(
        self,
        data: Any,
    ) -> dict:

        payload = {
            "provider": self.provider,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
            "ok": True,
        }
        return payload

    def _error(self, e: Exception | str) -> dict:
        return {
            "provider": self.provider,
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
        """Run a query. ``ok`` is False only for real failures: a query that matches
        nothing (HTTP 404 "No matches found!") returns ``ok=True`` with empty results.
        """
        endpoint = f"{self.BASE_URL}/{dataset.value}.json"
        params, _ = query.compile()

        if self.api_key:
            params["api_key"] = self.api_key

        # Build the query string by hand: terms use "+" for spaces and as the AND
        # separator, and ":*[]\"" are meaningful to OpenFDA. requests would encode
        # "+" as %2B and the API would answer 500.
        url = f"{endpoint}?{urlencode(params, quote_via=quote, safe=':+*[]\"')}"

        try:
            response = requests.get(url, timeout=self.timeout)
        except requests.RequestException as e:
            return self._error(e)

        if response.status_code == 404:
            return self._wrap_response(data={"meta": {}, "results": []})

        try:
            response.raise_for_status()
            return self._wrap_response(data=response.json())
        except Exception as e:
            detail = ""
            try:
                detail = response.json().get("error", {}).get("message", "")
            except ValueError:
                pass
            return self._error(f"{e} {detail}".strip())
