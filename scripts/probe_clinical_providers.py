"""
Probe the data providers that could feed the clinical_pipeline subagent.

Not part of the app or CI: it makes live API calls to check that each provider
method runs, returns sensible data, and behaves on edge cases (no match, obscure
company) *before* we wrap it as an agent tool. Raw responses are saved as JSON so
the real shape can be inspected when designing the tool's trimming.

Usage:
    uv run python scripts/probe_clinical_providers.py [--out DIR] [--only openfda,crl,...]

Needs OPENFDA_API_KEY and FINNHUB_API_KEY in .env. SEC probes need
SEC_EDGAR_IDENTITY ("Your Name your@email") in the environment, and are skipped otherwise.
"""

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from src.data_providers.openfda import Dataset  # noqa: E402
from src.data_providers.openfda import (OpenFDAAPIClient, Query,  # noqa: E402
                                        SearchClause, company_search_keys,
                                        matches_company)

# (ticker, company search name for OpenFDA, why it is in the set)
COMPANIES = [
    ("MRNA", "MODERNA", "large, many approvals"),
    ("VRTX", "VERTEX", "large, long approval history"),
    ("ALDX", "ALDEYRA", "small cap, has received a CRL"),
    ("CRVS", "CORVUS", "small cap, no approved drug"),
]

RESULTS: list[dict] = []
OUT_DIR = Path(tempfile.gettempdir()) / "clinical_probe"


def shape(obj, depth: int = 2):
    """Compact description of a JSON structure (keys, types, list lengths)."""
    if isinstance(obj, dict):
        if depth == 0:
            return f"dict({len(obj)} keys)"
        return {k: shape(v, depth - 1) for k, v in list(obj.items())[:25]}
    if isinstance(obj, list):
        if not obj:
            return "list(0)"
        return f"list({len(obj)}) of " + (
            json.dumps(shape(obj[0], depth - 1), default=str)[:300]
            if depth
            else type(obj[0]).__name__
        )
    if isinstance(obj, str):
        return f"str({len(obj)})"
    return type(obj).__name__


def record(name: str, resp, started: float, notes: list[str], count=None):
    elapsed = time.monotonic() - started
    raw = json.dumps(resp, default=str)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    safe = name.replace("/", "_").replace(" ", "_").replace(":", "_")
    (OUT_DIR / f"{safe}.json").write_text(json.dumps(resp, indent=2, default=str))
    ok = resp.get("ok") if isinstance(resp, dict) else None
    entry = {
        "name": name,
        "ok": ok,
        "seconds": round(elapsed, 2),
        "bytes": len(raw),
        "count": count,
        "notes": notes,
        "error": resp.get("error") if isinstance(resp, dict) else None,
    }
    RESULTS.append(entry)
    flag = "OK " if ok else "ERR"
    print(
        f"[{flag}] {name:<55} {entry['seconds']:>5}s {entry['bytes']:>9}B"
        f" count={count}"
    )
    for n in notes:
        print(f"        - {n}")
    if entry["error"]:
        print(f"        ! error: {entry['error'][:300]}")


def openfda_results(resp) -> list:
    if not resp.get("ok"):
        return []
    return resp.get("data", {}).get("results", []) or []


def probe_openfda(client: OpenFDAAPIClient):
    # 1. drugsfda by sponsor: approval history. Note the raw shape.
    for ticker, name, why in COMPANIES:
        t = time.monotonic()
        q = Query(
            search=[SearchClause("sponsor_name", f"{name}*")],
            limit=5,
        )
        resp = client.query(Dataset.DRUG_FDA, q)
        res = openfda_results(resp)
        notes = [why]
        if res:
            r0 = res[0]
            notes.append(f"top-level keys: {sorted(r0.keys())}")
            notes.append(
                f"sponsors seen: {sorted({r.get('sponsor_name') for r in res})}"
            )
            subs = r0.get("submissions") or []
            notes.append(
                f"first app {r0.get('application_number')}: "
                f"{len(subs)} submissions, products={len(r0.get('products') or [])}"
            )
        total = (resp.get("data") or {}).get("meta", {}).get("results", {}).get("total")
        notes.append(f"meta total={total}")
        record(f"openfda drugsfda sponsor={name}", resp, t, notes, count=total)

    # 2. Multi-clause AND: the existing Query joins with '+AND+' but requests
    # URL-encodes params, so '+' may arrive as %2B. Test explicitly.
    t = time.monotonic()
    q = Query(
        search=[
            SearchClause("sponsor_name", "VERTEX*"),
            SearchClause("submissions.submission_status", "AP"),
        ],
        limit=3,
    )
    resp = client.query(Dataset.DRUG_FDA, q)
    res = openfda_results(resp)
    record(
        "openfda drugsfda 2-clause AND (VERTEX*, approved)",
        resp,
        t,
        [f"got {len(res)} records; if ok=False see error"],
        count=len(res),
    )

    # 3. No-match behaviour: OpenFDA returns HTTP 404 for 0 results. The wrapper
    # turns that into ok=False, indistinguishable from a real outage.
    t = time.monotonic()
    q = Query(search=[SearchClause("sponsor_name", "ZZZNOSUCHCOMPANYZZZ")], limit=1)
    resp = client.query(Dataset.DRUG_FDA, q)
    record(
        "openfda drugsfda no-match behaviour",
        resp,
        t,
        ["expected: ok=True with empty results; check what we get"],
        count=0,
    )

    # 4. Complete response letters (rejections). Look at the real shape first.
    t = time.monotonic()
    resp = client.query(Dataset.TRANSPARENCY, Query(limit=2))
    res = openfda_results(resp)
    notes = []
    if res:
        notes.append(f"keys: {sorted(res[0].keys())}")
        notes.append("sample: " + json.dumps(res[0], default=str)[:500])
    total = (resp.get("data") or {}).get("meta", {}).get("results", {}).get("total")
    record("openfda transparency/crl shape", resp, t, notes, count=total)

    # 4b. CRLs per company (company_name is free text in the letter).
    for ticker, name, why in COMPANIES:
        t = time.monotonic()
        q = Query(
            search=[SearchClause("company_name", name)],
            sort="letter_date:desc",
            limit=5,
        )
        resp = client.query(Dataset.TRANSPARENCY, q)
        res = openfda_results(resp)
        notes = [why]
        for r in res:
            notes.append(
                f"{r.get('letter_date')} {r.get('approval_status')} "
                f"{r.get('letter_type')} app={r.get('application_number')} "
                f"company={r.get('company_name')!r} text_chars={len(r.get('text') or '')}"
            )
        record(f"openfda crl company={name}", resp, t, notes, count=len(res))

    # 5. Drug enforcement (recalls) by firm.
    for ticker, name, why in COMPANIES[:3]:
        t = time.monotonic()
        q = Query(
            search=[SearchClause("recalling_firm", f"{name}*")],
            sort="report_date:desc",
            limit=5,
        )
        resp = client.query(Dataset.DRUG_ENFORCEMENT, q)
        res = openfda_results(resp)
        notes = [why]
        if res:
            notes.append(f"keys: {sorted(res[0].keys())}")
            notes.append(
                "recent: "
                + str([(r.get("report_date"), r.get("classification")) for r in res])
            )
        total = (resp.get("data") or {}).get("meta", {}).get("results", {}).get("total")
        record(f"openfda enforcement firm={name}", resp, t, notes, count=total)

    # 6. Adverse events by brand name, top reactions (count query).
    t = time.monotonic()
    q = Query(
        search=[SearchClause("patient.drug.openfda.brand_name", "SPIKEVAX")],
        count="patient.reaction.reactionmeddrapt.exact",
    )
    resp = client.query(Dataset.DRUG_EVENT, q)
    res = openfda_results(resp)
    record(
        "openfda drug event top reactions brand=SPIKEVAX",
        resp,
        t,
        [f"top 3: {[(r.get('term'), r.get('count')) for r in res[:3]]}"],
        count=len(res),
    )


def probe_finnhub():
    from config import FINNHUB_API_KEY
    from src.data_providers.finnhub import FinnHubAPIClient

    client = FinnHubAPIClient(api_key=FINNHUB_API_KEY or "")
    t = time.monotonic()
    resp = client.fda_calendar()
    data = resp.get("data")
    notes = []
    if isinstance(data, list) and data:
        notes.append(f"keys: {sorted(data[0].keys())}")
        dates = sorted(d.get("fromDate", "") for d in data)
        notes.append(f"date range: {dates[0]} .. {dates[-1]}")
        notes.append("sample: " + json.dumps(data[0], default=str)[:300])
        for _, name, _ in COMPANIES:
            hits = [d for d in data if name.lower() in json.dumps(d).lower()]
            notes.append(f"mentions of {name}: {len(hits)}")
    elif isinstance(data, dict):
        notes.append(f"dict keys: {sorted(data.keys())}")
    record(
        "finnhub fda_calendar",
        resp,
        t,
        notes,
        count=len(data) if isinstance(data, list) else None,
    )

    for ticker, _, why in COMPANIES:
        t = time.monotonic()
        resp = client.company_profile2(ticker)
        d = resp.get("data") or {}
        record(
            f"finnhub company_profile2 {ticker}",
            resp,
            t,
            [f"name={d.get('name')!r} industry={d.get('finnhubIndustry')!r}"],
        )


def probe_sec():
    identity = os.environ.get("SEC_EDGAR_IDENTITY")
    if not identity:
        print("[SKIP] SEC probes: set SEC_EDGAR_IDENTITY='Your Name you@example.com'")
        return
    from src.data_providers.sec_edgar import SECEdgarClient

    client = SECEdgarClient(identity_email=identity)
    for ticker, _, why in COMPANIES:
        t = time.monotonic()
        resp = client.get_8k_data(ticker, limit=8)
        data = resp.get("data") or []
        notes = [why]
        if resp.get("ok"):
            mismatched = 0
            for f in data:
                parsed = [d["item_id"] for d in f.get("details") or []]
                declared = f["items_reported"]
                # items with no usable text are fine, but every declared item except
                # 9.01 should normally have parsed text
                missing = sorted(set(declared) - set(parsed))
                mismatched += bool(missing)
                chars = {d["item_id"]: len(d["content"]) for d in f["details"]}
                pr = len(f.get("press_release") or "")
                notes.append(
                    f"{f['filing_date'][:10]} declared={declared} "
                    f"chars={chars} press_release={pr} missing_text={missing}"
                )
            notes.append(
                f"filings where a declared item had no parsed text: {mismatched}/{len(data)}"
            )
        record(f"sec 8-K {ticker}", resp, t, notes, count=len(data))


NAME_SET = [
    "MRNA", "VRTX", "REGN", "GILD", "AMGN", "BIIB", "SRPT", "INCY",
    "EXEL", "ACAD", "CORT", "ARWR", "NVAX", "ALDX",
]  # fmt: skip


def search_name(profile_name: str) -> str:
    """First word of the company name, upper-cased, for a sponsor_name wildcard."""
    first = profile_name.split()[0] if profile_name else ""
    return "".join(ch for ch in first.upper() if ch.isalnum())


def probe_names(client: OpenFDAAPIClient):
    """How reliably does 'first word of the Finnhub name + *' find the right sponsor?"""
    from config import FINNHUB_API_KEY
    from src.data_providers.finnhub import FinnHubAPIClient

    finn = FinnHubAPIClient(api_key=FINNHUB_API_KEY or "")
    for ticker in NAME_SET:
        t = time.monotonic()
        prof = (finn.company_profile2(ticker).get("data") or {}).get("name") or ""
        name = search_name(prof)
        resp = client.query(
            Dataset.DRUG_FDA,
            Query(search=[SearchClause("sponsor_name", f"{name}*")], limit=100),
        )
        res = openfda_results(resp)
        sponsors = sorted({r.get("sponsor_name") for r in res})
        brands = sorted(
            {
                p.get("brand_name")
                for r in res
                for p in r.get("products") or []
                if p.get("marketing_status") != "Discontinued"
            }
        )
        crl = openfda_results(
            client.query(
                Dataset.TRANSPARENCY,
                Query(search=[SearchClause("company_name", name)], limit=100),
            )
        )
        record(
            f"names {ticker} -> {prof!r} -> {name}*",
            resp,
            t,
            [
                f"drugsfda apps={len(res)} sponsors={sponsors}",
                f"active brands (sample)={brands[:6]}",
                f"crl letters={len(crl)} companies={sorted({c.get('company_name') for c in crl})}",
            ],
            count=len(res),
        )


SAMPLE = [
    "MRNA", "VRTX", "REGN", "GILD", "AMGN", "BIIB", "SRPT", "INCY", "EXEL", "ACAD",
    "CORT", "ARWR", "NVAX", "ALDX", "CRVS", "ITCI", "BBIO", "ETNB", "IONS", "APLS",
    "MDGL", "INSM", "RARE", "ALNY", "NBIX", "BMRN", "ASND", "ARGX",
]  # fmt: skip


def _tokens(name: str) -> list[str]:
    import re

    return [t for t in re.split(r"[^A-Za-z0-9]+", name.upper()) if t]


def probe_sample(client: OpenFDAAPIClient):
    """Pass/fail validation across a wider set of biotechs. Prints a table."""
    from config import FINNHUB_API_KEY
    from src.data_providers.finnhub import FinnHubAPIClient

    finn = FinnHubAPIClient(api_key=FINNHUB_API_KEY or "")
    identity = os.environ.get("SEC_EDGAR_IDENTITY")
    sec = None
    if identity:
        from src.data_providers.sec_edgar import SECEdgarClient

        sec = SECEdgarClient(identity_email=identity)

    rows = []
    for ticker in SAMPLE:
        row = {"ticker": ticker, "issues": []}
        prof = (finn.company_profile2(ticker).get("data") or {}).get("name") or ""
        row["name"] = prof
        if not prof:
            row["issues"].append("EMPTY finnhub name")
            rows.append(row)
            continue
        keys = company_search_keys(prof)
        sponsors, apps = set(), 0
        for key in keys:
            r = client.query_all(
                Dataset.DRUG_FDA,
                Query(search=[SearchClause("sponsor_name", f"{key}*")]),
            )
            hits = [
                x
                for x in openfda_results(r)
                if matches_company(prof, x.get("sponsor_name"))
            ]
            dropped = {
                x.get("sponsor_name")
                for x in openfda_results(r)
                if not matches_company(prof, x.get("sponsor_name"))
            }
            if dropped:
                row.setdefault("filtered", []).append((key, sorted(dropped)))
            if r.get("truncated"):
                row["issues"].append(f"drugsfda truncated (key {key})")
            if hits:
                sponsors = {x.get("sponsor_name") for x in hits}
                apps = len(hits)
                break
        row["fda"] = (keys, apps, sorted(sponsors))
        cres, crl_key = [], None
        for key in keys:
            crl = client.query_all(
                Dataset.TRANSPARENCY,
                Query(
                    search=[SearchClause("company_name", key)], sort="letter_date:desc"
                ),
            )
            cres = [
                c
                for c in openfda_results(crl)
                if matches_company(prof, c.get("company_name"))
            ]
            if cres:
                crl_key = key
                break
        row["crl"] = (crl_key, len(cres))
        row["crl_status"] = sorted({c.get("approval_status") for c in cres})
        dates = [c.get("letter_date") for c in cres]
        try:
            from datetime import datetime as dt

            parsed = [dt.strptime(d, "%m/%d/%Y") for d in dates]
            if parsed != sorted(parsed, reverse=True):
                row["issues"].append("CRL not sorted by date desc")
        except Exception as e:
            row["issues"].append(f"CRL date parse: {e}")
        if sec:
            t = time.monotonic()
            r8 = sec.get_8k_data(ticker, limit=25)
            row["8k_seconds"] = round(time.monotonic() - t, 1)
            if not r8.get("ok"):
                row["issues"].append(f"8-K error: {r8.get('error')}")
            else:
                filings = r8["data"]
                row["8k"] = len(filings)
                bad = []
                for f in filings:
                    parsed_ids = {d["item_id"] for d in f["details"]}
                    missing = set(f["items_reported"]) - parsed_ids - {"9.01"}
                    if not f["items_reported"] or missing:
                        bad.append(
                            (
                                f["filing_date"][:10],
                                f["items_reported"],
                                sorted(missing),
                            )
                        )
                    # Only earnings (2.02) reliably come with an EX-99 press release;
                    # 7.01/8.01 are often in the body text itself.
                    if "2.02" in f["items_reported"] and not f.get("press_release"):
                        row.setdefault("no_press_release", []).append(
                            f["filing_date"][:10]
                        )
                row["8k_bad"] = bad
                if not filings:
                    row["issues"].append("no 8-K filings (foreign filer?)")
                if bad:
                    row["issues"].append(f"{len(bad)} 8-Ks with unparsed items")
        rows.append(row)

    print("\n===== SAMPLE VALIDATION =====")
    for r in rows:
        print(f"\n{r['ticker']:<5} {r['name']!r}")
        for k in ("fda_joined", "fda_token", "crl", "crl_status", "8k", "8k_seconds"):
            if k in r:
                print(f"   {k}: {r[k]}")
        if (
            r.get("sponsors_joined") != r.get("sponsors_token")
            and "sponsors_token" in r
        ):
            print(
                f"   sponsors joined={r.get('sponsors_joined')}\n            token ={r.get('sponsors_token')}"
            )
        elif r.get("sponsors_joined"):
            print(f"   sponsors: {r['sponsors_joined']}")
        if r.get("no_press_release"):
            print(f"   8-Ks with 2.02 but NO press release: {r['no_press_release']}")
        for b in r.get("8k_bad", [])[:3]:
            print(f"   8-K unparsed: {b}")
        for i in r["issues"]:
            print(f"   ISSUE: {i}")
    n_issue = sum(bool(r["issues"]) for r in rows)
    print(f"\n{len(rows)} companies, {n_issue} with at least one issue")
    (OUT_DIR).mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "_sample.json").write_text(json.dumps(rows, indent=2, default=str))


def crl_stats(client: OpenFDAAPIClient):
    """What does the whole CRL dataset look like? (Is it rejections only?)"""
    import collections

    r = client.query_all(Dataset.TRANSPARENCY, Query(), max_records=1000)
    res = openfda_results(r)
    print(
        f"\n===== CRL DATASET ===== total={r.get('total')} fetched={len(res)} truncated={r.get('truncated')}"
    )
    print(
        "approval_status:", collections.Counter(x.get("approval_status") for x in res)
    )
    print("letter_type:", collections.Counter(x.get("letter_type") for x in res))
    years = collections.Counter(x.get("letter_year") for x in res)
    print("letter_year:", sorted(years.items(), key=lambda kv: str(kv[0])))
    lens = sorted(len(x.get("text") or "") for x in res)
    print(
        f"text chars: min={lens[0]} median={lens[len(lens)//2]} max={lens[-1]} empty={sum(l == 0 for l in lens)}"
    )
    print(
        "application_number types:",
        collections.Counter(type(x.get("application_number")).__name__ for x in res),
    )


def main():
    global OUT_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", help="directory for raw JSON responses")
    parser.add_argument(
        "--only", help="comma list of: openfda,finnhub,sec,names,sample,crlstats"
    )
    args = parser.parse_args()
    if args.out:
        OUT_DIR = Path(args.out)
    only = set((args.only or "openfda,finnhub,sec").split(","))

    print(f"raw responses -> {OUT_DIR}\n")
    if "openfda" in only:
        probe_openfda(OpenFDAAPIClient(api_key=os.environ.get("OPENFDA_API_KEY", "")))
    if "finnhub" in only:
        probe_finnhub()
    if "sec" in only:
        probe_sec()
    if "sample" in only:
        probe_sample(OpenFDAAPIClient(api_key=os.environ.get("OPENFDA_API_KEY", "")))
    if "crlstats" in only:
        crl_stats(OpenFDAAPIClient(api_key=os.environ.get("OPENFDA_API_KEY", "")))
    if "names" in only:
        probe_names(OpenFDAAPIClient(api_key=os.environ.get("OPENFDA_API_KEY", "")))

    failed = [r for r in RESULTS if not r["ok"]]
    print(f"\n{len(RESULTS)} calls, {len(failed)} returned ok=False")
    (OUT_DIR / "_summary.json").write_text(json.dumps(RESULTS, indent=2, default=str))


if __name__ == "__main__":
    main()
