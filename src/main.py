# # from massive import RESTClient
# from alpha_vantage.timeseries import TimeSeries
# from alpha_vantage.techindicators import TechIndicators
# from alpha_vantage.alphaintelligence import AlphaIntelligence
# from alpha_vantage.econindicators import EconIndicators
# from alpha_vantage.alphavantage import AlphaVantage
# from alpha_vantage.fundamentaldata import FundamentalData

from fredapi import Fred
from dotenv import load_dotenv
from os import getenv
import requests
load_dotenv()
key = getenv("MARKETSTACK_API_KEY")
test = requests.get(f"http://api.marketstack.com/v2/eod?access_key={key}&symbols=AAPL")

print(test.json())
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


