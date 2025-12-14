from datetime import datetime, date, timezone
from typing import Any, Dict, List, Optional, Union

from massive import RESTClient


class MassiveAPIClient:
    """
    Thin Python wrapper for MassiveAPIClient. Converts Python object to a dictionary and returns relevant metadata in JSON friendly format.
    """

    def __init__(self, api_key: str):
        self.api_key = RESTClient(api_key=api_key)

    def get_aggs(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        from_: str | int | datetime | date,
        to: str | int | datetime | date,
        adjusted: bool | None = None,
        sort: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Args:

            ticker: The ticker symbol.
            multiplier: The size of the timespan multiplier.
            timespan: The size of the time window.
            from_: The start of the aggregate time window as YYYY-MM-DD, a date, Unix MS Timestamp, or a datetime.
            to: The end of the aggregate time window as YYYY-MM-DD, a date, Unix MS Timestamp, or a datetime.
            adjusted: Whether or not the results are adjusted for splits. By default, results are adjusted. Set this to false to get results that are NOT adjusted for splits.
            sort:  Sort the results by timestamp. asc will return results in ascending order (oldest at the top), desc will return results in descending order (newest at the top).The end of the aggregate time window.
            limit: Limits the number of base aggregates queried to create the aggregate results. Max 50000 and Default 5000.
        """
        try:
            aggs = self.api_key.get_aggs(
                ticker=ticker,
                multiplier=multiplier,
                timespan=timespan,
                from_=from_,
                to=to,
                adjusted=adjusted,
                sort=sort,
                limit=limit,
            )

            aggs_json = [a.__dict__ if not isinstance(a, dict) else a for a in aggs]

            return {
                "provider": "massive",
                "endpoint": "get_aggs",
                "ticker": ticker,
                "fetched_at": datetime.now().isoformat(sep=" "),
                "raw": aggs_json,
            }
        except Exception as e:
            return {
                "provider": "massive",
                "endpoint": "get_aggs",
                "ticker": ticker,
                "fetched_at": datetime.now().isoformat(sep=" "),
                "raw": [],
                "error": str(e),
            }
