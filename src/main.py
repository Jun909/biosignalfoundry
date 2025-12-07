# from massive import RESTClient
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.alphaintelligence import AlphaIntelligence
from alpha_vantage.econindicators import EconIndicators
from alpha_vantage.alphavantage import AlphaVantage
from alpha_vantage.fundamentaldata import FundamentalData
from dotenv import load_dotenv
from os import getenv
load_dotenv()

ts = TimeSeries(key=getenv("ALPHAVANTAGE_API_KEY"))
ti = TechIndicators(key=getenv("ALPHAVANTAGE_API_KEY"))
ai = AlphaIntelligence(key=getenv("ALPHAVANTAGE_API_KEY"))
ei = EconIndicators(key=getenv("ALPHAVANTAGE_API_KEY"))
fd = FundamentalData(key=getenv("ALPHAVANTAGE_API_KEY"))

ticker = "AAPL"

# functions = [func for func in dir(fd) if not func.startswith('_')]
# print(functions)

# ['', '', '', '', '', '', '', '', '', '', 'get_splits',

print(fd.get_splits(symbol=ticker))
