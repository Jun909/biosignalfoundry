from os import getenv

from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(getenv("REDIS_PORT", 6379))
REDIS_DB = int(getenv("REDIS_DB", 0))
REDIS_CACHE_TTL_SECONDS_MARKETSTACK = 604800
REDIS_CACHE_TTL_SECONDS_ALPHAVANTAGE = 86400

ALPHAVANTAGE_API_KEY = getenv("ALPHAVANTAGE_API_KEY")
FINNHUB_API_KEY = getenv("FINNHUB_API_KEY")
