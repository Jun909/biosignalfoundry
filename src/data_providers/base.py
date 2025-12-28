from datetime import date, datetime, timezone
from typing import Any, Dict, Optional
import requests

import pandas as pd


class BaseClient:
    """
    Base client class providing common serialization and response formatting
    methods for API clients.
    TODO: Add rate limiting and caching mechanisms.
    """

    def _serialize(self, obj: Any) -> Any:
        if obj is None:
            return None

        elif isinstance(obj, (str, int, float, bool, bytes)):
            return obj

        elif isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}

        elif isinstance(obj, pd.DataFrame):
            return [
                {k: self._serialize(v) for k, v in row.items()}
                for row in obj.to_dict(orient="records")
            ]

        elif isinstance(obj, pd.Series):
            return self._serialize_series(obj)

        elif isinstance(obj, (list, tuple)):
            return [self._serialize(item) for item in obj]

        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()

        elif hasattr(obj, "__dict__"):
            return {
                k: self._serialize(v)
                for k, v in obj.__dict__.items()
                if not k.startswith("_")
            }

        return obj

    def _make_response(
        self,
        provider: str,
        endpoint: str,
        result: Any,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        payload = {
            "provider": provider,
            "endpoint": endpoint,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": self._serialize(result),
            "ok": True,
        }

        if extra:
            payload.update(extra)

        return payload

    def _call(
        self, client: Any, provider: str, endpoint: str, *args, **kwargs
    ) -> Dict[str, Any]:
        try:
            func = getattr(client, endpoint)
            result = func(*args, **kwargs)
            extra = {}
            if "ticker" in kwargs:
                extra["ticker"] = kwargs.get("ticker")

            elif "symbol" in kwargs:
                extra["ticker"] = kwargs.get("symbol")

            elif "series_id" in kwargs:
                extra["series_id"] = kwargs.get("series_id")

            elif args and isinstance(args[0], str):
                extra["ticker"] = args[0]

            return self._make_response(provider, endpoint, result, extra=extra)

        except Exception as e:
            resp = {
                "provider": provider,
                "endpoint": endpoint,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "data": [],
                "ok": False,
                "error": str(e),
            }
            if "ticker" in kwargs:
                resp["ticker"] = kwargs.get("ticker")

            elif "symbol" in kwargs:
                resp["ticker"] = kwargs.get("symbol")

            return resp

    def _serialize_series(self, series: pd.Series) -> Any:
        """
        Serialize a pandas Series into a JSON-serializable format.
        """
        # If the series index is datetime-like, produce a list of {"date": ..., "value": ...}
        if pd.api.types.is_datetime64_any_dtype(series.index):
            result = []
            for index, value in series.items():
                if pd.isna(index):  # type: ignore
                    date_str = None
                elif isinstance(index, (datetime, date)):
                    date_str = index.isoformat()
                else:
                    date_str = str(index)

                if isinstance(value, (int, float)):
                    val = value
                elif isinstance(value, (pd.Timestamp, datetime, date)):
                    val = value.isoformat()
                else:
                    val = self._serialize(value)

                result.append({"date": date_str, "value": val})

            # Deduplicate by date
            seen_dates = set()
            deduped = []
            for r in result:
                d = r.get("date")
                if d not in seen_dates:
                    deduped.append(r)
                    seen_dates.add(d)

            return deduped

        # Otherwise, treat as a metadata Series and return a dict of key -> serialized value
        return {str(k): self._serialize(v) for k, v in series.items()}
