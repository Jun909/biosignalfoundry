from collections.abc import Iterable
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Union


class BaseClient:
    """
    Base client class providing common serialization and response formatting
    methods for API clients.
    """

    def _serialize(self, obj: Any) -> Any:
        if obj is None:
            return None
        if isinstance(obj, (dict, str, bytes)):
            return obj
        if isinstance(obj, Iterable):
            out = []
            for v in obj:
                if isinstance(v, dict):
                    out.append(v)
                elif hasattr(v, "__dict__"):
                    out.append(
                        {k: getattr(v, k) for k in v.__dict__ if not k.startswith("_")}
                    )
                else:
                    out.append(v)
            return out
        if hasattr(obj, "__dict__"):
            return {k: getattr(obj, k) for k in obj.__dict__ if not k.startswith("_")}
        return obj

    def _make_response(
        self, endpoint: str, result: Any, extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        payload = {
            "provider": "massive",
            "endpoint": endpoint,
            "fetched_at": datetime.now().isoformat(sep=" "),
            "data": self._serialize(result),
        }
        if extra:
            payload.update(extra)
        return payload

    def _call(self, api_key: Any, endpoint: str, *args, **kwargs) -> Dict[str, Any]:
        try:
            func = getattr(api_key, endpoint)
            result = func(*args, **kwargs)
            extra = {}
            if "ticker" in kwargs:
                extra["ticker"] = kwargs.get("ticker")
            elif args and isinstance(args[0], str):
                extra["ticker"] = args[0]
            return self._make_response(endpoint, result, extra=extra)

        except Exception as e:
            resp = {
                "provider": "massive",
                "endpoint": endpoint,
                "fetched_at": datetime.now().isoformat(sep=" "),
                "data": [],
                "error": str(e),
            }
            if "ticker" in kwargs:
                resp["ticker"] = kwargs.get("ticker")
            return resp
