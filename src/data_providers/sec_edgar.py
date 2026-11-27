# clients/sec_edgar.py
import re
from datetime import datetime, timezone

import pandas as pd
from edgar import Company, set_identity

from config import REDIS_CACHE_TTL_SECONDS_SEC_EDGAR

from .base import BaseClient
from .cache import cached_call

# regex for s-3
SHELF_AMOUNT_RE = re.compile(
    r"Proposed\s+maximum\s+aggregate\s+offering\s+price.*?"
    r"\$?\s*(?P<amount>[\d,.]+)"
    r"\s*(?P<scale>million|billion|trillion)?",
    re.IGNORECASE | re.DOTALL,
)
ATM_RE = re.compile(
    r"at[- ]the[- ]market\s+(?:offering|issuance|program)|equity\s+distribution\s+agreement|sales\s+agreement\s+(?:with|between)",
    re.IGNORECASE,
)
USE_OF_PROCEEDS_RE = re.compile(
    r"use\s+of\s+proceeds[\s\.]+(.{1,500})", re.IGNORECASE | re.DOTALL
)
SECURITIES_RE = re.compile(
    r"\b(common\s+stock|preferred\s+stock|warrants?|debt\s+securities|units|depositary\s+shares)\b",
    re.IGNORECASE,
)
RULE_415_RE = re.compile(r"Rule 415", re.IGNORECASE)

# regex for 10-K
ITEM_1A_START = re.compile(r"ITEM\s+1A[\.\s\-:]+RISK\s+FACTORS", re.IGNORECASE)
ITEM_7_START = re.compile(
    r"ITEM\s+7[\.\s\-:]+MANAGEMENT.*?DISCUSSION\s+AND\s+ANALYSIS",
    re.IGNORECASE | re.DOTALL,
)
NEXT_ITEM_RE = re.compile(r"ITEM\s+\d+[A-Z]?[\.\s\-:]+", re.IGNORECASE)

# regex for 10-Q
ITEM_2_Q_START = re.compile(
    r"ITEM\s+2[\.\s\-:]+MANAGEMENT.*?DISCUSSION\s+AND\s+ANALYSIS",
    re.IGNORECASE | re.DOTALL,
)
PART_II_1A_START = re.compile(
    r"PART\s+II.*?ITEM\s+1A[\.\s\-:]+RISK\s+FACTORS", re.IGNORECASE | re.DOTALL
)
NEXT_ITEM_Q_RE = re.compile(r"ITEM\s+\d+[A-Z]?[\.\s\-:]+|PART\s+II", re.IGNORECASE)

# regex for 8-K
# An item heading sits at the start of a line ("Item 8.01. Other Events."). Anchoring to
# the line start skips in-text cross references ("...in Item 1.01 of this Report").
ITEM_8K_HEADING_RE = re.compile(
    # [^\S\n] = any whitespace but a newline: filers use thin/nbsp spaces after "Item"
    r"^[^\S\n]*Item[^\S\n]+(?P<item_id>\d\.\d{2})\.?[^\S\n]*(?P<title>[^\n]*)$",
    re.IGNORECASE | re.MULTILINE,
)
SIGNATURE_RE = re.compile(
    r"^[^\S\n]*SIGNATURES?[^\S\n]*$", re.IGNORECASE | re.MULTILINE
)

ITEM_MAP = {
    "1.01": "Material Definitive Agreement",
    "1.02": "Termination of Material Agreement",
    "2.01": "Acquisition/Disposition of Assets",
    "2.02": "Earnings Release (Results of Operations)",
    "2.03": "Creation of Direct Financial Obligation",
    "2.05": "Restructuring Costs",
    "2.06": "Material Impairments",
    "3.01": "Delisting or Listing Standard Notice",
    "3.02": "Unregistered Sales of Equity Securities",
    "4.01": "Change of Auditor",
    "5.02": "Director/Officer Changes",
    "5.07": "Shareholder Vote Results",
    "7.01": "Regulation FD Disclosure",
    "8.01": "Other Events",
    "9.01": "Financial Statements and Exhibits",
}

# Items whose substance usually lives in an attached press release (EX-99.x).
PRESS_RELEASE_ITEMS = {"2.02", "7.01", "8.01"}


class SECEdgarClient(BaseClient):
    """
    Thin wrapper around edgartools SDK with normalized outputs.
    """

    def __init__(self, identity_email: str):
        set_identity(identity_email)
        self.provider = "sec_edgartools"

    def _normalize_usd_amount(self, value: str | None, scale: str | None) -> int:
        """
        Normalizes SEC currency strings (e.g., '1,200.50', 'million') into a base integer.
        """
        if not value:
            return 0

        try:
            # Clean commas and any stray whitespace
            clean_value = value.replace(",", "").strip()
            amount = float(clean_value)

            if scale:
                # Map scales to multipliers
                multipliers = {
                    "thousand": 1_000,
                    "million": 1_000_000,
                    "billion": 1_000_000_000,
                    "trillion": 1_000_000_000_000,
                }
                factor = multipliers.get(scale.strip().lower(), 1)
                amount *= factor

            return int(amount)

        except (ValueError, TypeError):
            return 0

    def _fetch_exhibit_text(self, filing):
        """Returns the text of the first press-release exhibit (EX-99.x), if any."""
        try:
            for doc in filing.attachments:
                if str(getattr(doc, "document_type", "")).upper().startswith("EX-99"):
                    return doc.text()[:20000]
        except Exception:
            return None
        return None

    def _normalize_form4_data(self, df: pd.DataFrame) -> list[dict]:
        records = []

        for _, row in df.iterrows():
            raw_date = row.get("Date")

            if isinstance(raw_date, pd.Timestamp):
                date_iso = (
                    raw_date.tz_localize("UTC").isoformat()
                    if raw_date.tzinfo is None
                    else raw_date.isoformat()
                )

            elif isinstance(raw_date, (int, float)):
                date_iso = datetime.fromtimestamp(
                    raw_date / 1000, tz=timezone.utc
                ).isoformat()

            elif isinstance(raw_date, str) and raw_date:
                date_iso = pd.to_datetime(raw_date, errors="coerce")
                date_iso = date_iso.isoformat() if not pd.isna(date_iso) else None
            else:
                date_iso = None

            records.append(
                {
                    "transaction_type": row.get("Transaction Type"),
                    "code": row.get("Code"),
                    "shares": int(row["Shares"]) if row.get("Shares") else None,
                    "price": float(row["Price"]) if row.get("Price") else None,
                    "date": date_iso,
                    "insider": row.get("Insider"),
                    "position": row.get("Position") or None,
                    "remaining_shares": (
                        int(row["Remaining Shares"])
                        if row.get("Remaining Shares")
                        else None
                    ),
                }
            )

        return records

    def _extract_s3_data(self, clean_text: str):
        """
        Method to extract data from raw S-3 document to check shelf, ATM(at-the-market), securities and proceeds
        """
        shelf_match = SHELF_AMOUNT_RE.search(clean_text)
        if shelf_match:
            raw_amount = shelf_match.group("amount")
            raw_scale = shelf_match.group("scale")
            shelf_amount = self._normalize_usd_amount(raw_amount, raw_scale)
        else:
            shelf_amount = None

        has_rule_415 = bool(RULE_415_RE.search(clean_text))

        has_atm = bool(ATM_RE.search(clean_text))

        securities = list(
            set(s.lower().replace(" ", "_") for s in SECURITIES_RE.findall(clean_text))
        )

        use_match = USE_OF_PROCEEDS_RE.search(clean_text)
        use_of_proceeds = use_match.group(0) if use_match else None

        return shelf_amount, has_atm, securities, use_of_proceeds, has_rule_415

    def _extract_10k_data(self, clean_text: str):
        """
        Extracts key narrative sections from the 10-K.
        """
        sections = {
            "risk_factors": ITEM_1A_START,
            "management_discussion": ITEM_7_START,
        }
        extracted = {}

        for key, pattern in sections.items():
            match = pattern.search(clean_text)
            if match:
                start_idx = match.start()
                next_match = NEXT_ITEM_RE.search(clean_text, start_idx + 100)

                if next_match:
                    end_idx = next_match.start()
                    content = clean_text[start_idx:end_idx].strip()
                else:
                    content = clean_text[start_idx : start_idx + 10000].strip()
                extracted[key] = re.sub(r"\s+", " ", content)
            else:
                extracted[key] = None

        return extracted

    def _extract_10q_data(self, clean_text: str):
        sections = {
            "quarterly_mda": ITEM_2_Q_START,
            "quarterly_risks": PART_II_1A_START,
        }
        extracted = {}

        for key, pattern in sections.items():
            match = pattern.search(clean_text)
            if match:
                start_idx = match.start()
                next_match = NEXT_ITEM_Q_RE.search(clean_text, start_idx + 100)

                if next_match:
                    end_idx = next_match.start()
                    content = clean_text[start_idx:end_idx].strip()
                else:
                    content = clean_text[start_idx : start_idx + 8000].strip()

                extracted[key] = re.sub(r"\s+", " ", content)
            else:
                extracted[key] = None

        return extracted

    def _extract_8k_data(self, raw_text: str):
        text = raw_text.replace("\r", "")
        matches = list(ITEM_8K_HEADING_RE.finditer(text))
        signature = SIGNATURE_RE.search(text, matches[-1].end()) if matches else None
        text_end = signature.start() if signature else len(text)

        extracted_items = []
        seen_ids = set()
        # Headings stacked with no text between them ("Item 2.02 ... / Item 7.01 ...")
        # share the body that follows, so they wait here for it.
        pending: list = []

        for i, match in enumerate(matches):
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else text_end
            raw_content = text[match.end() : end_idx].strip()
            pending.append(match)

            if len(raw_content) < 20:
                continue

            content = re.sub(r"\s+", " ", raw_content)
            for head in pending:
                item_id = head.group("item_id")
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                extracted_items.append(
                    {
                        "item_id": item_id,
                        "display_name": ITEM_MAP.get(item_id, "Other Material Event"),
                        "title": head.group("title").strip().rstrip("."),
                        "content": content,
                    }
                )
            pending = []

        return extracted_items, sorted(seen_ids)

    def get_form4_data(
        self, ticker: str, limit: int = 10
    ) -> dict[str, str | dict | bool | list]:
        try:
            company = Company(ticker)
            filings = company.get_filings(form="4").head(limit)

            df = pd.concat(
                [f.obj().to_dataframe().fillna("") for f in filings]  # type: ignore
            )

            normalized = self._normalize_form4_data(df)

            return self._make_response(
                provider=self.provider,
                endpoint="form4_transactions",
                result=normalized,
                extra={"ticker": ticker},
            )

        except Exception as e:
            return self._make_error(
                self.provider, "form4_transactions", e, extra={"ticker": ticker}
            )

    def get_s3_data(self, ticker: str, limit: int = 10):
        try:
            company = Company(ticker)
            filings = company.get_filings(form="S-3").head(limit)

            if not filings:
                return self._make_response(
                    provider=self.provider,
                    endpoint="s3",
                    result=None,
                    extra={"ticker": ticker},
                )

            latest = sorted(filings, key=lambda f: f.filing_date, reverse=True)[0]

            raw_text = latest.text()
            clean_text = re.sub(r"\s+", " ", raw_text)

            shelf_amount, has_atm, securities, use_of_proceeds, has_rule_415 = (
                self._extract_s3_data(clean_text=clean_text)
            )
            filing_date = datetime.combine(
                latest.filing_date, datetime.min.time(), tzinfo=timezone.utc
            )
            result = {
                "form": latest.form,
                "filing_date": filing_date.isoformat(),
                "accession_number": latest.accession_number,
                "is_shelf": (shelf_amount is not None) or has_rule_415,
                "shelf_amount_usd": shelf_amount,
                "has_atm": has_atm,
                "securities": securities,
                "use_of_proceeds": use_of_proceeds,
                "amended": latest.form.endswith("/A"),
                "confidence": 0.7 if shelf_amount else 0.4,
            }

            return self._make_response(
                provider=self.provider,
                endpoint="s3",
                result=result,
                extra={"ticker": ticker},
            )

        except Exception as e:
            return self._make_error(self.provider, "s3", e, extra={"ticker": ticker})

    def get_10k_data(self, ticker: str):
        try:
            company = Company(ticker)
            # We usually only want the single most recent annual report
            filings = company.get_filings(form="10-K").head(5)

            if not filings:
                return self._make_response(
                    provider=self.provider,
                    endpoint="10k",
                    result=None,
                    extra={"ticker": ticker},
                )

            # Get the latest one
            latest = sorted(filings, key=lambda f: f.filing_date, reverse=True)[0]

            # 10-Ks are massive; we clean whitespace but keep some structure
            raw_text = latest.text()
            clean_text = re.sub(r"\s+", " ", raw_text)

            sections = self._extract_10k_data(clean_text=clean_text)

            filing_date = datetime.combine(
                latest.filing_date, datetime.min.time(), tzinfo=timezone.utc
            )

            result = {
                "form": latest.form,
                "filing_date": filing_date.isoformat(),
                "accession_number": latest.accession_number,
                "risk_factors_preview": (
                    (sections["risk_factors"][:500] + "...")
                    if sections["risk_factors"]
                    else None
                ),
                "mda_preview": (
                    (sections["management_discussion"][:500] + "...")
                    if sections["management_discussion"]
                    else None
                ),
                "full_sections": {
                    "item_1a": sections["risk_factors"],
                    "item_7": sections["management_discussion"],
                },
                "is_amended": latest.form.endswith("/A"),
            }

            return self._make_response(
                provider=self.provider,
                endpoint="10k",
                result=result,
                extra={"ticker": ticker},
            )

        except Exception as e:
            return self._make_error(self.provider, "10k", e, extra={"ticker": ticker})

    def get_10q_data(self, ticker: str):
        try:
            company = Company(ticker)
            # Get the 3rd most recent 10-Qs (to ensure we get the latest one)
            filings = company.get_filings(form="10-Q").head(3)

            if not filings:
                return self._make_response(
                    provider=self.provider,
                    endpoint="10q",
                    result=None,
                    extra={"ticker": ticker},
                )

            # Sort by date and take the latest
            latest = sorted(filings, key=lambda f: f.filing_date, reverse=True)[0]

            raw_text = latest.text()
            clean_text = re.sub(r"\s+", " ", raw_text)

            sections = self._extract_10q_data(clean_text=clean_text)

            filing_date = datetime.combine(
                latest.filing_date, datetime.min.time(), tzinfo=timezone.utc
            )

            result = {
                "form": latest.form,
                "filing_date": filing_date.isoformat(),
                "accession_number": latest.accession_number,
                "mda_content": sections["quarterly_mda"],
                "risk_factors_content": sections["quarterly_risks"],
                # Logic check: did they actually update risks or just refer to the 10-K?
                "risks_updated": "no material changes"
                not in (sections["quarterly_risks"] or "").lower(),
                "amended": latest.form.endswith("/A"),
            }

            return self._make_response(
                provider=self.provider,
                endpoint="10q",
                result=result,
                extra={"ticker": ticker},
            )

        except Exception as e:
            return self._make_error(self.provider, "10q", e, extra={"ticker": ticker})

    def get_8k_data(self, ticker: str, limit: int = 5):
        return cached_call(
            f"sec_edgar:8k:{ticker.upper()}:{limit}",
            REDIS_CACHE_TTL_SECONDS_SEC_EDGAR,
            lambda: self._fetch_8k_data(ticker, limit),
        )

    def _fetch_8k_data(self, ticker: str, limit: int):
        try:
            company = Company(ticker)
            filings = company.get_filings(form="8-K").head(limit)

            if not filings:
                return self._make_response(
                    provider=self.provider,
                    endpoint="8k",
                    result=[],
                    extra={"ticker": ticker},
                )

            results = []
            for filing in filings:
                # 1. Parse the item sections out of the filing text
                items, parsed_ids = self._extract_8k_data(filing.text())

                # 2. The filing's own item list is authoritative; the parsed ids are
                # the fallback (and show which items had usable text).
                declared = [
                    i.strip() for i in (filing.items or "").split(",") if i.strip()
                ]
                item_ids = sorted(declared) or parsed_ids

                # 3. The announcement itself is usually an attached press release
                press_release = None
                if PRESS_RELEASE_ITEMS & set(item_ids):
                    exhibit = self._fetch_exhibit_text(filing)
                    if exhibit:
                        press_release = re.sub(r"\s+", " ", exhibit)

                filing_date = datetime.combine(
                    filing.filing_date, datetime.min.time(), tzinfo=timezone.utc
                )

                # 4. Construct the direct SEC URL
                # Note: primary_document is the correct attribute; cik must be 10 digits
                cik_padded = str(company.cik).zfill(10)
                acc_no_clean = filing.accession_number.replace("-", "")
                url = f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/{acc_no_clean}/{filing.primary_document}"

                results.append(
                    {
                        "filing_date": filing_date.isoformat(),
                        "accession_number": filing.accession_number,
                        "items_reported": item_ids,
                        "details": items,
                        "press_release": press_release,
                        "is_amended": filing.form.endswith("/A"),
                        "url": url,
                    }
                )

            return self._make_response(
                provider=self.provider,
                endpoint="8k",
                result=results,
                extra={"ticker": ticker},
            )

        except Exception as e:
            return self._make_error(self.provider, "8k", e, extra={"ticker": ticker})

    def get_13f_data(self, manager_name_or_cik: str):
        try:
            company = Company(manager_name_or_cik)
            # Get the latest 13F-HR filing and parse the object
            thirteen_f = company.get_filings(form="13F-HR").latest().obj()

            # Access the holdings DataFrame directly
            holdings_df = thirteen_f.holdings  # type: ignore

            if holdings_df.empty:
                return {"ok": True, "data": []}

            # Convert to list of dictionaries (one dict per row)
            holdings_list = holdings_df.to_dict(orient="records")

            # Optional: Add portfolio weights and clean values
            total_val = holdings_df["Value"].sum()

            for item in holdings_list:
                # SEC reports value in thousands; multiply by 1000 for actual USD
                item["value_usd"] = float(item["Value"]) * 1000
                item["weight_pct"] = (
                    round((float(item["Value"]) / total_val) * 100, 2)
                    if total_val > 0
                    else 0
                )
                item["SharesPrnAmount"] = int(item["SharesPrnAmount"])
                item["SoleVoting"] = int(item["SoleVoting"])
                item["SharedVoting"] = int(item["SharedVoting"])
                item["NonVoting"] = int(item["NonVoting"])
                item["PutCall"] = item.get("PutCall", "").upper()

            result = {
                "manager_name": thirteen_f.manager_name,
                "total_holdings": len(holdings_list),
                "holdings": holdings_list,
                "report_date": thirteen_f.filing_date,
            }

            return self._make_response(
                provider=self.provider,
                endpoint="13f",
                result=result,
                extra={"cik": company.cik},
            )

        except Exception as e:
            return self._make_error(
                self.provider,
                "13f",
                e,
                extra={"manager_name_or_cik": manager_name_or_cik},
            )
