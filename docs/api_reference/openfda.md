# OpenFDA

OpenFDA's API documentation can be found here:
https://open.fda.gov/apis/drug/event/example-api-queries/

An api wrapper has been implemented to accomodate Elasticsearch-based API : src/data_providers/openfda.py

Four classes used:

* SearchClause: gather arguments (field,term) that are needed in Query
* Query - collect arguments accordingly and pass them to OpenFDAAPIClient as params dict.
* OpenFDAAPIClient - fetches the data from openFDA and return an output.
* Dataset - Fixed keywords needed depending on the query subject

Here are some examples to use openFDA client:

---
## Initialization

```python
from src.data_providers.openfda import OpenFDAAPIClient, Dataset, Query, SearchClause

openfda_client = OpenFDAAPIClient(api_key=key or "")
```

## Basic usage

### Example 1:
With "search" and "limit" parameters:
```python
myquery = Query(
    search=[SearchClause(field="brand_name", term="child")],
    limit=1
)

myoutput = openfda_client.query(dataset=Dataset.DRUG_NDC, query=myquery)
```
### Output:
```json
{
  "provider": "OpenFDA",
  "fetched_at": "2026-01-01T19:54:34.784621+00:00",
  "ok": true,
  "data": {
    "meta": {
      "disclaimer": "Do not rely on openFDA to make decisions regarding medical care. While we make every effort to ensure that data is accurate, you should assume all results are unvalidated. We may limit or otherwise restrict your access to the API in line with our Terms of Service.",
      "terms": "https://open.fda.gov/terms/",
      "license": "https://open.fda.gov/license/",
      "last_updated": "2025-12-31",
      "results": {
        "skip": 0,
        "limit": 1,
        "total": 2
      }
    },
    "results": [
      {
        "product_ndc": "62670-6637",
        "product_id": "62670-6637_1a9f05a2-4a90-aa88-e063-6394a90a452a",
        "brand_name": "Anti Bacterial Hand Gel Flower Child",
        "brand_name_base": "Anti Bacterial Hand Gel",
        "brand_name_suffix": "Flower Child",
        "generic_name": "Alcohol",
        "labeler_name": "Bath & Body Works, Inc.",
        "marketing_category": "OTC MONOGRAPH DRUG",
        "product_type": "HUMAN OTC DRUG",
        "dosage_form": "GEL",
        "route": ["TOPICAL"],
        "finished": true,
        "application_number": "505G(a)(3)",
        "marketing_start_date": "20240108",
        "marketing_end_date": "20270108",
        "active_ingredients": [
          {
            "name": "ALCOHOL",
            "strength": "71 mL/100mL"
          }
        ],
        "packaging": [
          {
            "package_ndc": "62670-6637-0",
            "description": "29 mL in 1 BOTTLE (62670-6637-0)",
            "marketing_start_date": "20240108",
            "marketing_end_date": "20270108",
            "sample": false
          }
        ],
        "openfda": {
          "manufacturer_name": ["Bath & Body Works, Inc."],
          "rxcui": ["2282911"],
          "spl_set_id": ["1a9ef8eb-325f-8c42-e063-6394a90a1ecc"],
          "spl_id": "1a9f05a2-4a90-aa88-e063-6394a90a452a",
          "is_original_packager": [true],
          "unii": ["3K9958V90M"]
        }
      }
    ]
  }  
}

```

### Example 2:
Only using parameter "limit":
```python
myquery = Query(
    limit=1
)

myoutput = openfda_client.query(dataset=Dataset.TOBACCO_PROBLEM, query=myquery)
```
### Output:
```json
{
  "provider": "OpenFDA",
  "fetched_at": "2026-01-01T20:01:10.526410+00:00",
  "ok": true,
  "data": {
    "meta": {
      "disclaimer": "Do not rely on openFDA to make decisions regarding medical care. While we make every effort to ensure that data is accurate, you should assume all results are unvalidated. We may limit or otherwise restrict your access to the API in line with our Terms of Service.",
      "terms": "https://open.fda.gov/terms/",
      "license": "https://open.fda.gov/license/",
      "last_updated": "2025-12-11",
      "results": {
        "skip": 0,
        "limit": 1,
        "total": 1314
      }
    },
    "results": [
      {
        "report_id": 2158073,
        "date_submitted": "06/12/2024",
        "nonuser_affected": "No",
        "number_tobacco_products": 1,
        "number_health_problems": 1,
        "number_product_problems": 0,
        "reported_health_problems": [
          "Shortness of breath"
        ],
        "reported_product_problems": [
          "No information provided"
        ],
        "tobacco_products": [
          "Electronic cigarette or vaping product (for example, E-cigarette, vape or vape pen, personal vaporizer, cigalike, e-pen, hookah pen, mod, e-cigar, e-hookah, and e-pipe; E-liquid (also known as \"e-juice\" or \"vape juice\"))"
        ]
      }
    ]
  }
}

```

### Example 3:

Using "search", "date_filter" and "limit" parameters:

Note: a date range term (e.g "[20180101+TO+20200723]") is passed as is. The `date_filter` argument is kept for compatibility but no longer needed: the client builds the query string itself, so `+`, `:`, `*`, `[` and `]` are never URL-encoded.
```python
myquery = Query(
    search=[SearchClause(field="date_submitted", term="[20180101+TO+20200723]")],
    date_filter=True,
    limit=1
)

myoutput = openfda_client.query(dataset=Dataset.TOBACCO_PROBLEM, query=myquery)
```
### Output:
```json
{
  "provider": "OpenFDA",
  "fetched_at": "2026-01-01T20:04:33.902460+00:00",
  "ok": true,
  "data": {
    "meta": {
      "disclaimer": "Do not rely on openFDA to make decisions regarding medical care. While we make every effort to ensure that data is accurate, you should assume all results are unvalidated. We may limit or otherwise restrict your access to the API in line with our Terms of Service.",
      "terms": "https://open.fda.gov/terms/",
      "license": "https://open.fda.gov/license/",
      "last_updated": "2025-12-11",
      "results": {
        "skip": 0,
        "limit": 1,
        "total": 847
      }
    },
    "results": [
      {
        "report_id": 2083649,
        "date_submitted": "05/09/2020",
        "nonuser_affected": "Yes",
        "number_tobacco_products": 1,
        "number_health_problems": 4,
        "number_product_problems": 1,
        "reported_health_problems": [
          "Respiratory compromise",
          "Fever",
          "Generalised chest pain",
          "Cough"
        ],
        "reported_product_problems": [
          "Other"
        ],
        "tobacco_products": [
          "Electronic cigarette or vaping product (also known as E-cigarette, vape pen, hookah pen, mod, e-cigar, e-hookah, and e-pipe; E-liquid (also known as \"e-juice\" or \"vape juice\"))"
        ]
      }
    ]
  }
}

```
### Example 4:

Using "search", "limit" and "count" parameters:

```python
myquery = Query(
    search=[SearchClause(field="patient.drug.openfda.pharm_class_epc", term="nonsteroidal+anti-inflammatory+drug")],
    limit=1,
    count="patient.reaction.reactionmeddrapt.exact"
)

myoutput = openfda_client.query(dataset=Dataset.DRUG_EVENT, query=myquery)
```
### Output

JSON output, truncated:

```json
{
  "provider": "OpenFDA",
  "fetched_at": "2026-01-01T20:10:55.947811+00:00",
  "ok": true,
  "data": {
    "meta": {
      "disclaimer": "Do not rely on openFDA to make decisions regarding medical care. While we make every effort to ensure that data is accurate, you should assume all results are unvalidated. We may limit or otherwise restrict your access to the API in line with our Terms of Service.",
      "terms": "https://open.fda.gov/terms/",
      "license": "https://open.fda.gov/license/",
      "last_updated": "2025-10-30"
    },
    "results": [
      { "term": "DRUG INEFFECTIVE", "count": 136875 },
      { "term": "OFF LABEL USE", "count": 108372 },
      { "term": "INTENTIONAL PRODUCT USE ISSUE", "count": 16607 },
      { "term": "CONTUSION", "count": 16558 }
    ]
  }
}

```

---
## Behaviour worth knowing

Verified against the live API (see `scripts/probe_clinical_providers.py`).

* **No match is not an error.** openFDA answers HTTP 404 "No matches found!" when a search matches nothing. The client returns `ok: true` with `data.results == []`. `ok: false` is only for real failures; the error text never contains the API key.
* **Truncation.** `query()` returns at most `limit` records (default 100). Responses include `total` and `truncated` (True when `skip + returned < total`). Use `openfda_client.query_all(dataset, query, max_records=1000)` to page through all matches; it returns one merged response and sets `truncated` if matches remain beyond `max_records`.
* **Caching.** Successful `query()` results are cached in Redis for a day (`openfda:<dataset>:<hash of the query>`); failures are not cached.
* **Multi-clause searches** join with `+AND+` and work (`sponsor_name:VERTEX*+AND+submissions.submission_status:AP`).
* **Sponsor and company names are not tokenized in `drug/drugsfda`.** `sponsor_name:VERTEX` finds nothing, `sponsor_name:VERTEX*` finds `VERTEX PHARMS` and `VERTEX PHARMS INC`. Use a wildcard on the first word of the company name. `company_search_keys("Intra-Cellular Therapies Inc")` returns `["INTRACELLULAR", "INTRA"]`; search with each and keep the hits for which `matches_company(name, sponsor)` is true (it requires a whole-word match, so `INTRABIO` is rejected).
* **`drug/drugsfda` has no biologics.** Only NDAs and ANDAs. Moderna and Novavax (BLA/vaccine products) return nothing, so "no results" does not mean "no approvals".
* **`drug/drugsfda` is large.** About 10KB per application, mostly `SUPPL` (supplement) submissions. Trim before handing it to an LLM.
* **`transparency/crl` (complete response letters)** holds 466 letters, 2002-2025 (mostly recent). 312 have `approval_status: Approved` (the application was approved later), 154 `Unapproved`. `letter_type` includes `COMPLETE RESPONSE` (453), `TENTATIVE APPROVAL`, `REFUSAL TO FILE` and a few others. `text` is OCR output with redaction artifacts (median about 8.7K characters). `letter_date` is `MM/DD/YYYY`; `application_number` is a list. The `company_name` field is free text from the letter.
* **`drug/enforcement` (recalls)** is mostly manufacturing issues (Pfizer: 158 records, e.g. subpotent drug), rarely relevant to a small biotech.
* **`drug/event`** is keyed by drug name, not company, and biologics and vaccines often have no records.
