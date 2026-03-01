# clients/sec_edgar.py
import re
from datetime import datetime, timezone

import pandas as pd
from edgar import Company, set_identity

from .base import BaseClient

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
ITEM_8K_RE = re.compile(
    r"Item\s+(?P<item_id>\d\.\d{2})[\.\s\-:]+(?P<title>.*?)(?=Item\s+\d\.\d{2}|SIGNATURES|EXHIBIT\s+INDEX|$)",
    re.IGNORECASE | re.DOTALL,
)

ITEM_MAP = {
    "1.01": "Material Definitive Agreement",
    "2.01": "Acquisition/Disposition of Assets",
    "2.02": "Earnings Release (Results of Operations)",
    "5.02": "Director/Officer Changes",
    "8.01": "Other Events",
    "9.01": "Financial Statements and Exhibits",
}


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
        """Finds Exhibit 99.1 and returns its text content."""
        try:
            for doc in filing.attachments:
                if (
                    "ex99" in doc.name.lower()
                    or "exhibit 99" in doc.description.lower()
                ):
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
        matches = list(ITEM_8K_RE.finditer(text))

        extracted_items = []
        seen_ids = set()

        for i, match in enumerate(matches):
            item_id = match.group("item_id")

            start_idx = match.end()  # Start after the Title
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            raw_content = text[start_idx:end_idx].strip()

            if "...." in raw_content[:50] or len(raw_content) < 20:
                continue

            extracted_items.append(
                {
                    "item_id": item_id,
                    "display_name": ITEM_MAP.get(item_id, "Other Material Event"),
                    "title": match.group("title").strip().split("\n")[0],
                    "content": re.sub(r"\s+", " ", raw_content),
                }
            )
            seen_ids.add(item_id)

        return extracted_items, sorted(list(seen_ids))

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
            return {
                "provider": self.provider,
                "endpoint": "form4_transactions",
                "ticker": ticker,
                "fetched_at": self._serialize(None),
                "data": [],
                "ok": False,
                "error": str(e),
            }

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
            return {
                "provider": self.provider,
                "endpoint": "s3",
                "ticker": ticker,
                "ok": False,
                "data": None,
                "error": str(e),
            }

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
            return {
                "provider": self.provider,
                "endpoint": "10k",
                "ticker": ticker,
                "ok": False,
                "data": None,
                "error": str(e),
            }

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
            return {
                "provider": self.provider,
                "endpoint": "10q",
                "ticker": ticker,
                "ok": False,
                "data": None,
                "error": str(e),
            }

    def get_8k_data(self, ticker: str, limit: int = 5):
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
                # 1. Get the text directly from the filing object
                raw_text = filing.text()

                # 2. Extract specific Items (1.01, 2.02, etc)
                items, item_ids = self._extract_8k_data(raw_text)

                if "2.02" in item_ids or "8.01" in item_ids:
                    exhibit_content = self._fetch_exhibit_text(filing)
                    if exhibit_content:
                        for item in items:
                            if item["item_id"] in ["2.02", "8.01"]:
                                # We replace the boring legal text with the actual announcement
                                item["content"] = (
                                    f"[FULL PRESS RELEASE]: {re.sub(r'\s+', ' ', exhibit_content)}"
                                )

                filing_date = datetime.combine(
                    filing.filing_date, datetime.min.time(), tzinfo=timezone.utc
                )

                # 3. Construct the direct SEC URL
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
            return {
                "ok": False,
                "error": str(e),
                "ticker": ticker,
                "provider": self.provider,
                "endpoint": "8k",
            }

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
            # return {"ok": False, "error": str(e), "query": manager_name_or_cik}
            return {
                "provider": self.provider,
                "endpoint": "13f",
                "manager name or cik": manager_name_or_cik,
                "ok": False,
                "data": None,
                "error": str(e),
            }
