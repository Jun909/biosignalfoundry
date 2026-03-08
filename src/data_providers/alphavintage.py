import json

from alpha_vantage.alphaintelligence import AlphaIntelligence
from alpha_vantage.econindicators import EconIndicators
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries

from config import REDIS_CACHE_TTL_SECONDS_ALPHAVANTAGE
from src.core.redis_client import redis_client

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

    def get_monthly(self, ticker: str):
        return self._call(
            self.client_time_series,
            self.provider,
            "get_monthly",
            symbol=ticker,
        )

    def get_monthly_adjusted(self, ticker: str):
        return self._call(
            self.client_time_series,
            self.provider,
            "get_monthly_adjusted",
            symbol=ticker,
        )

    def get_quote_endpoint(self, ticker: str, entitlement: str | None = None):
        """
        Args:
            ticker (str): The stock ticker symbol.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data
                or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_time_series,
            self.provider,
            "get_quote_endpoint",
            symbol=ticker,
            entitlement=entitlement,
        )

    def get_symbol_search(self, keywords: str):
        """
        Args:
            keywords (str): The keywords to query on
        """
        return self._call(
            self.client_time_series,
            self.provider,
            "get_symbol_search",
            keywords=keywords,
        )

    def get_weekly(self, ticker: str):
        return self._call(
            self.client_time_series,
            self.provider,
            "get_weekly",
            symbol=ticker,
        )

    def get_weekly_adjusted(self, ticker: str):
        return self._call(
            self.client_time_series,
            self.provider,
            "get_weekly_adjusted",
            symbol=ticker,
        )

    def get_ad(
        self,
        ticker: str,
        interval: str = "daily",
        month: str | None = None,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            month (str | None): None by default.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_ad",
            symbol=ticker,
            interval=interval,
            month=month,
            entitlement=entitlement,
        )

    def get_adosc(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_adosc",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_adx(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_adx",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_adxr(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_adxr",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_apo(
        self,
        ticker: str,
        interval: str = "daily",
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_apo",
            symbol=ticker,
            interval=interval,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_aroon(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_aroon",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_aroonosc(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_aroonosc",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_atr(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_atr",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_bbands(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_bbands",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_cci(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_cci",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_cmo(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_cmo",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_dema(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_dema",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_dx(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_dx",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_ema(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_ema",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_ht_dcperiod(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_ht_dcperiod",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_ht_dcphase(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_ht_dcphase",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_ht_phasor(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_ht_phasor",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_ht_sine(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_ht_sine",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_ht_trendline(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_ht_trendline",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_ht_trendmode(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_ht_trendmode",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_kama(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_kama",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_macdext(
        self,
        ticker: str,
        interval: str = "daily",
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_macdext",
            symbol=ticker,
            interval=interval,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_mama(
        self,
        ticker: str,
        interval: str = "daily",
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_mama",
            symbol=ticker,
            interval=interval,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_mfi(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_mfi",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_midpoint(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_midpoint",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_midprice(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_midprice",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_minus_di(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_minus_di",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_minus_dm(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_minus_dm",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_mom(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_mom",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_natr(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_natr",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_obv(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_obv",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_plus_di(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_plus_di",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_plus_dm(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_plus_dm",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_ppo(
        self,
        ticker: str,
        interval: str = "daily",
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_ppo",
            symbol=ticker,
            interval=interval,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_roc(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_roc",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_rocr(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_rocr",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_rsi(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_rsi",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_sar(
        self,
        ticker: str,
        interval: str = "daily",
        acceleration: float | None = None,
        maximum: float | None = None,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            acceleration (float | None): The acceleration factor for the Parabolic SAR. None by default.
            maximum (float | None): The maximum value for the Parabolic SAR. None by default.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_sar",
            symbol=ticker,
            interval=interval,
            acceleration=acceleration,
            maximum=maximum,
            entitlement=entitlement,
        )

    def get_sma(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_sma",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_stoch(
        self,
        ticker: str,
        interval: str = "daily",
        fastkperiod: int | None = None,
        slowkperiod: int | None = None,
        slowdperiod: int | None = None,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            fastkperiod (int | None): The time period for the fast %K line. None by default.
            slowkperiod (int | None): The time period for the slow %K line. None by default.
            slowdperiod (int | None): The time period for the %D line. None by default.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_stoch",
            symbol=ticker,
            interval=interval,
            fastkperiod=fastkperiod,
            slowkperiod=slowkperiod,
            slowdperiod=slowdperiod,
            entitlement=entitlement,
        )

    def get_stochf(
        self,
        ticker: str,
        interval: str = "daily",
        fastkperiod: int | None = None,
        fastdperiod: int | None = None,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            fastkperiod (int | None): The time period for the fast %K line. None by default.
            fastdperiod (int | None): The time period for the fast %D line. None by default.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_stochf",
            symbol=ticker,
            interval=interval,
            fastkperiod=fastkperiod,
            fastdperiod=fastdperiod,
            entitlement=entitlement,
        )

    def get_stochrsi(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_stochrsi",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_t3(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_t3",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_tema(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_tema",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_trange(
        self, ticker: str, interval: str = "daily", entitlement: str | None = None
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_trange",
            symbol=ticker,
            interval=interval,
            entitlement=entitlement,
        )

    def get_trima(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_trima",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_trix(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_trix",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_ultosc(
        self,
        ticker: str,
        interval: str = "daily",
        timeperiod1: int | None = None,
        timeperiod2: int | None = None,
        timeperiod3: int | None = None,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            timeperiod1 (int | None): The first time period for the Ultimate Oscillator. None by default.
            timeperiod2 (int | None): The second time period for the Ultimate Oscillator. None by default.
            timeperiod3 (int | None): The third time period for the Ultimate Oscillator. None by default.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_ultosc",
            symbol=ticker,
            interval=interval,
            timeperiod1=timeperiod1,
            timeperiod2=timeperiod2,
            timeperiod3=timeperiod3,
            entitlement=entitlement,
        )

    def get_willr(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_willr",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            entitlement=entitlement,
        )

    def get_wma(
        self,
        ticker: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
        entitlement: str | None = None,
    ):
        """
        Args:
            ticker (str): The stock ticker symbol.
            interval (str): The time interval between two consecutive data points. Supported values are '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'.
            time_period (int): The number of data points used to calculate each value.
            series_type (str): The desired price type in the time series. Supported values are 'close', 'open', 'high', 'low'.
            entitlement (str | None): Supported values are 'realtime' for realtime US stock market data or 'delayed' for 15-minute delayed US stock market data
        """
        return self._call(
            self.client_tech_indicators,
            self.provider,
            "get_wma",
            symbol=ticker,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            entitlement=entitlement,
        )

    def get_most_active(self):
        return self._call(
            self.client_alpha_intelligence,
            self.provider,
            "get_most_active",
        )

    def get_top_gainers(self):
        return self._call(
            self.client_alpha_intelligence,
            self.provider,
            "get_top_gainers",
        )

    def get_top_losers(self):
        return self._call(
            self.client_alpha_intelligence,
            self.provider,
            "get_top_losers",
        )

    def get_cpi(self, interval: str = "monthly"):
        """
        Args:
            interval (str): Supported values are 'monthly' and 'semiannual'
        """
        return self._call(
            self.client_econ_indicators,
            self.provider,
            "get_cpi",
            interval=interval,
        )

    def get_durables(self):
        return self._call(
            self.client_econ_indicators,
            self.provider,
            "get_durables",
        )

    def get_ffr(self, interval: str = "monthly"):
        """
        Args:
            interval (str): Supported values are 'daily', 'weekly', and 'monthly'
        """
        return self._call(
            self.client_econ_indicators,
            self.provider,
            "get_ffr",
            interval=interval,
        )

    def get_inflation(self):
        return self._call(
            self.client_econ_indicators,
            self.provider,
            "get_inflation",
        )

    def get_nonfarm(self):
        return self._call(
            self.client_econ_indicators,
            self.provider,
            "get_nonfarm",
        )

    def get_real_gdp(self, interval: str = "annual"):
        """
        Args:
            interval (str): Supported values are 'annual' and 'quarterly'
        """
        return self._call(
            self.client_econ_indicators,
            self.provider,
            "get_real_gdp",
            interval=interval,
        )

    def get_real_gdp_per_capita(self):
        return self._call(
            self.client_econ_indicators,
            self.provider,
            "get_real_gdp_per_capita",
        )

    def get_retail_sales(self):
        return self._call(
            self.client_econ_indicators,
            self.provider,
            "get_retail_sales",
        )

    def get_treasury_yield(self, interval: str = "daily", maturity: str = "10year"):
        """
        Args:
            interval (str): Supported values are 'daily', 'weekly', and 'monthly'
            maturity (str): Supported values are '3month', '6month', '1year', '2year', '3year', '5year', '7year', '10year', '20year', and '30year'
        """
        return self._call(
            self.client_econ_indicators,
            self.provider,
            "get_treasury_yield",
            interval=interval,
            maturity=maturity,
        )

    def get_unemployment(self):
        return self._call(
            self.client_econ_indicators,
            self.provider,
            "get_unemployment",
        )

    def get_balance_sheet_annual(self, ticker: str):
        return self._call(
            self.client_fundamental_data,
            self.provider,
            "get_balance_sheet_annual",
            symbol=ticker,
        )

    def get_balance_sheet_quarterly(self, ticker: str):
        return self._call(
            self.client_fundamental_data,
            self.provider,
            "get_balance_sheet_quarterly",
            symbol=ticker,
        )

    def get_cash_flow_annual(self, ticker: str):
        return self._call(
            self.client_fundamental_data,
            self.provider,
            "get_cash_flow_annual",
            symbol=ticker,
        )

    def get_cash_flow_quarterly(self, ticker: str):
        return self._call(
            self.client_fundamental_data,
            self.provider,
            "get_cash_flow_quarterly",
            symbol=ticker,
        )

    def get_company_overview(self, ticker: str):
        return self._call(
            self.client_fundamental_data,
            self.provider,
            "get_company_overview",
            symbol=ticker,
        )

    def get_dividends(self, ticker: str):
        return self._call(
            self.client_fundamental_data,
            self.provider,
            "get_dividends",
            symbol=ticker,
        )

    def get_earnings_annual(self, ticker: str):
        return self._call(
            self.client_fundamental_data,
            self.provider,
            "get_earnings_annual",
            symbol=ticker,
        )

    def get_earnings_quarterly(self, ticker: str):
        return self._call(
            self.client_fundamental_data,
            self.provider,
            "get_earnings_quarterly",
            symbol=ticker,
        )

    def get_income_statement_annual(self, ticker: str):
        cache_key = f"alphavantage:get_income_statement_annual:{ticker}"
        cache_data = redis_client.get(cache_key)
        if cache_data:
            return json.loads(cache_data)  # type: ignore

        result = self._call(
            self.client_fundamental_data,
            self.provider,
            "get_income_statement_annual",
            symbol=ticker,
        )

        # cache it regardless of error or not
        redis_client.setex(
            cache_key, REDIS_CACHE_TTL_SECONDS_ALPHAVANTAGE, json.dumps(result)
        )

        return result

    def get_splits(self, ticker: str):
        return self._call(
            self.client_fundamental_data,
            self.provider,
            "get_splits",
            symbol=ticker,
        )
