# clients/sec_edgar.py
import re
from datetime import datetime, timezone

import pandas as pd
from edgar import Company, set_identity

from .base import BaseClient

SHELF_AMOUNT_RE = re.compile(
    r"Proposed\s+maximum\s+aggregate\s+offering\s+price.*?"  
    r"\$?\s*(?P<amount>[\d,.]+)"                             
    r"\s*(?P<scale>million|billion|trillion)?"               
    , re.IGNORECASE | re.DOTALL
)
ATM_RE = re.compile(
    r"at[- ]the[- ]market\s+(?:offering|issuance|program)|equity\s+distribution\s+agreement|sales\s+agreement\s+(?:with|between)",
    re.IGNORECASE
)

USE_OF_PROCEEDS_RE = re.compile(
    r"use\s+of\s+proceeds[\s\.]+(.{1,500})",
    re.IGNORECASE | re.DOTALL
)

SECURITIES_RE = re.compile(
    r"\b(common\s+stock|preferred\s+stock|warrants?|debt\s+securities|units|depositary\s+shares)\b",
    re.IGNORECASE
)

RULE_415_RE = re.compile(r"Rule 415", re.IGNORECASE)

ISSUER_FORM_MAP = {
    "us_domestic": {
        "registration": ["S-3", "S-3/A", "ATM", "424B"],
        "annual": ["10-K"],
        "quarterly": ["10-Q"],
        "events": ["8-K"],
        "insider": ["4"],
    },
    "foreign_private_issuer": {
        "registration": ["F-3", "F-3/A"],
        "annual": ["20-F"],
        "events": ["6-K"],
        "insider": [],
    },
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
                    "trillion": 1_000_000_000_000
                }
                factor = multipliers.get(scale.strip().lower(), 1)
                amount *= factor
                
            return int(amount)
        
        except (ValueError, TypeError):
            return 0
    
    def _extract_s3_data(self, clean_text: str):
        """
        Method to extract data from raw S-3 document to check shelf, ATM(at-the-market), securities and proceeds
        """
        shelf_match = SHELF_AMOUNT_RE.search(clean_text)
        if shelf_match:
            raw_amount = shelf_match.group('amount')
            raw_scale = shelf_match.group('scale')
            shelf_amount = self._normalize_usd_amount(raw_amount, raw_scale)
        else:
            shelf_amount = None

        has_rule_415 = bool(RULE_415_RE.search(clean_text))

        has_atm = bool(ATM_RE.search(clean_text))

        securities = list(
            set(
                s.lower().replace(" ", "_")
                for s in SECURITIES_RE.findall(clean_text)
            )
        )

        use_match = USE_OF_PROCEEDS_RE.search(clean_text)
        use_of_proceeds = use_match.group(0) if use_match else None

        return shelf_amount, has_atm, securities, use_of_proceeds, has_rule_415



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
                # epoch milliseconds fallback
                date_iso = datetime.fromtimestamp(
                    raw_date / 1000, tz=timezone.utc
                ).isoformat()

            elif isinstance(raw_date, str) and raw_date:
                # last-resort string parsing
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

    def get_s3_data(self, ticker: str, limit:int = 10):
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
            
            latest = sorted(
                filings, key=lambda f: f.filing_date, reverse=True
            )[0]

            raw_text = latest.text()
            clean_text = re.sub(r"\s+", " ", raw_text)

            shelf_amount, has_atm, securities, use_of_proceeds, has_rule_415 = self._extract_s3_data(clean_text=clean_text)
            filing_date = datetime.combine(latest.filing_date, datetime.min.time(), tzinfo=timezone.utc)
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
        