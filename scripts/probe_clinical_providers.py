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

from src.data_providers.openfda import (
    Dataset,  # noqa: E402
    OpenFDAAPIClient,
    Query,
    SearchClause,
)

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


def main():
    global OUT_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", help="directory for raw JSON responses")
    parser.add_argument("--only", help="comma list of: openfda,finnhub,sec,names")
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
    if "names" in only:
        probe_names(OpenFDAAPIClient(api_key=os.environ.get("OPENFDA_API_KEY", "")))

    failed = [r for r in RESULTS if not r["ok"]]
    print(f"\n{len(RESULTS)} calls, {len(failed)} returned ok=False")
    (OUT_DIR / "_summary.json").write_text(json.dumps(RESULTS, indent=2, default=str))


if __name__ == "__main__":
    main()
