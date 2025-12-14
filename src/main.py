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
load_dotenv()

# ts = TimeSeries(key=getenv("ALPHAVANTAGE_API_KEY"))
# ti = TechIndicators(key=getenv("ALPHAVANTAGE_API_KEY"))
# ai = AlphaIntelligence(key=getenv("ALPHAVANTAGE_API_KEY"))
# ei = EconIndicators(key=getenv("ALPHAVANTAGE_API_KEY"))
# fd = FundamentalData(key=getenv("ALPHAVANTAGE_API_KEY"))


fred = Fred(api_key=getenv("FRED_API_KEY"))
ticker = "AAPL"
series = "SP500"

# functions = [func for func in dir(fred) if not func.startswith('_')]
# print(functions)


# '', '', 'get_series_latest_release', 'get_series_vintage_dates', 
# 'latest_realtime_end', 'max_results_per_request', 'nan_char', 'proxies', 'root_url', 'search', 
# 'search_by_category', 'search_by_release']

print(fred.get_series_latest_release(series_id=series))


