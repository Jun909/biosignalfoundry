# EDGARTOOLS

Open-sourced project: https://github.com/dgunning/edgartools

Docs: https://edgartools.readthedocs.io/en/latest/

We need it mainly for the following documents:


## US based companies

* Form 4 - Insider intent (Good if insiders buy more shares of the company)
* S-3 - Dilution risk (Sell/Avoid if the company cannot survive the next 12 months without dilution)
* 8-K - Sudden events ("Breaking news" that is enough to affect the stock price)
* 10-Q / 10-K - Cash runway, survival (10-Q: Quarter update of the company, 10-K: Annual document of the company)
* 13F - Just for confirmation (Quarterly filing of institutional investment manager, catch: can have 45 days delay of reporting after the quarter ends)

## Non-US based companies
* F-3 - 
* 20-F - Cash runway, survival (Annual document of the company)
* 6-K - Sudden events

**Note**: only the 8-K path (`get_8k_data`) has been validated so far. Form 4, S-3, 10-K, 10-Q and 13F are unchanged and still need the same kind of checking (they rely on regexes over filing text).

## Setup
`SECEdgarClient(identity_email=...)` needs a declared contact for the SEC (`SEC_EDGAR_IDENTITY` in `.env` is what the probe script uses); `edgartools` refuses to call EDGAR without one.

## 8-K (`get_8k_data`)
Validated on 28 biotechs (about 25 filings each) with `scripts/probe_clinical_providers.py --only sample`.

* `items_reported` comes from the filing's own item list (`filing.items`). `details` has the parsed section text per item, which is checked against that list.
* Headings are matched at the start of a line and tolerate thin and non-breaking spaces (`Item\u20098.01`). Items listed back to back with one shared body (Item 2.02 followed by Item 7.01) get that same body.
* `press_release` is the text of the `EX-99.x` exhibit, only fetched for items 2.02, 7.01 and 8.01. Many 7.01/8.01 and some 2.02 filings put the text in the body and have no exhibit, so `press_release` can be `None`.
* Known gap: an 8-K/A whose explanatory note mentions an item without its own heading has no parsed text for that item (1 of about 700 filings in the sample).
* Companies without 8-Ks: foreign private issuers (20-F/6-K, e.g. Ascendis, argenx) return an empty list; unknown or delisted tickers return `ok: false` ("Company not found").
* Items can be long (a contract item was 13KB) and `press_release` up to 20,000 characters, so trim before handing it to an LLM.
* Cached in Redis for 6 hours per `(ticker, limit)`.
