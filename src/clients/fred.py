from collections.abc import Iterable
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Union

from fredapi import Fred

from .base import BaseClient


class FredAPIClient(BaseClient):
    """
    Thin Python wrapper for FredAPIClient. Converts SDK objects to plain
    dictionaries and returns metadata in a JSON-friendly structure.
    FRED takes in series_id as parameter for most functions.
    Example of series_id: "CPIAUCSL", "GDP", "UNRATE", "FEDFUNDS" etc
    """

    def __init__(self, api_key: str):
        self.client = Fred(api_key=api_key)
        self.provider = "fred"

    def get_series(
        self,
        series_id: str,
        observation_start: str | datetime | date | None = None,
        observation_end: str | datetime | date | None = None,
    ):
        return self._call(
            self.client,
            self.provider,
            "get_series",
            series_id=series_id,
            observation_start=observation_start,
            observation_end=observation_end,
        )
    
    def get_series_all_releases(self, series_id: str, realtime_start: str | date | datetime | None = None, realtime_end: str | date | datetime | None = None):
        return self._call(
            self.client,
            self.provider,
            "get_series_all_releases",
            series_id=series_id,
            realtime_start=realtime_start,
            realtime_end=realtime_end,
        )
    
    def get_series_as_of_date(self, series_id: str, as_of_date: str | date | datetime):
        return self._call(
            self.client,
            self.provider,
            "get_series_as_of_date",
            series_id=series_id,
            as_of_date=as_of_date,
        )
    
    def get_series_first_release(self, series_id: str):
        return self._call(
            self.client,
            self.provider,
            "get_series_first_release",
            series_id=series_id,
        )
    
    def get_series_info(self, series_id: str):
        return self._call(
            self.client,
            self.provider,
            "get_series_info",
            series_id=series_id,
        )
    
    def get_series_latest_release(self, series_id: str):
        return self._call(
            self.client,
            self.provider,
            "get_series_latest_release",
            series_id=series_id,
        )
    def get_series_vintage_dates(self, series_id: str):
        return self._call(
            self.client,
            self.provider,
            "get_series_vintage_dates",
            series_id=series_id,
        )
