from collections.abc import Iterable
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Union

from alpha_vantage.alphaintelligence import AlphaIntelligence
from alpha_vantage.econindicators import EconIndicators
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries

from .base import BaseClient


class AlphaVintageAPIClient(BaseClient):
    """
    Thin Python wrapper for AlphaVintageAPIClient. Converts SDK objects to plain
    dictionaries and returns metadata in a JSON-friendly structure.
    AlphaVintage takes in ticker as parameter for most functions.
    Example of ticker: "AAPL", "GOOGL", "MSFT", "AMZN" etc
    """

    def __init__(self, api_key: str):
        self.client_time_series = TimeSeries(key=api_key)
        self.client_tech_indicators = TechIndicators(key=api_key)
        self.client_alpha_intelligence = AlphaIntelligence(key=api_key)
        self.client_econ_indicators = EconIndicators(key=api_key)
        self.client_fundamental_data = FundamentalData(key=api_key)
        self.provider = "alphavintage"

    def get_daily(self, ticker: str, outputsize: str = "compact"):
        return self._call(
            self.client_time_series,
            self.provider,
            "get_daily",
            symbol=ticker,
            outputsize=outputsize,
        )

    def get_market_status(self):
        return self._call(
            self.client_time_series,
            self.provider,
            "get_market_status",
        )
