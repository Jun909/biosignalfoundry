# # from massive import RESTClient
# from alpha_vantage.timeseries import TimeSeries
# from alpha_vantage.techindicators import TechIndicators
# from alpha_vantage.alphaintelligence import AlphaIntelligence
# from alpha_vantage.econindicators import EconIndicators
# from alpha_vantage.alphavantage import AlphaVantage
# from alpha_vantage.fundamentaldata import FundamentalData

from os import getenv

import requests
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()
key = getenv("MARKETSTACK_API_KEY")
# test = requests.get(f"http://api.marketstack.com/v2/eod?access_key={key}&symbols=AAPL")

# print(test.json())
# ts = TimeSeries(key=getenv("ALPHAVANTAGE_API_KEY"))
# ti = TechIndicators(key=getenv("ALPHAVANTAGE_API_KEY"))
# ai = AlphaIntelligence(key=getenv("ALPHAVANTAGE_API_KEY"))
# ei = EconIndicators(key=getenv("ALPHAVANTAGE_API_KEY"))
# fd = FundamentalData(key=getenv("ALPHAVANTAGE_API_KEY"))


# fred = Fred(api_key=getenv("FRED_API_KEY"))
ticker = "AAPL"
series = "SP500"

# functions = [func for func in dir(fred) if not func.startswith('_')]
# print(functions)

# print(fred.nan_char(series_id="CPIAUCSL"))

import os

from clients.massive import MassiveAPIClient

massiveclient = MassiveAPIClient(api_key=os.getenv("MASSIVE_API_KEY"))
print(
    massiveclient.get_aggs(
        ticker=ticker,
        multiplier=1,
        timespan="minute",
        from_="2025-11-01",
        to="2025-12-01",
        limit=10,
    )
)
