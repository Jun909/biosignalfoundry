# MARKETSTACK

Here are the functions available under the free-tier API for Marketstack. Each section lists the function name and a sample output (truncated for brevity).

More info: https://marketstack.com/pricing

For API documentation, check: https://marketstack.com/documentation_v2

A simple python wrapper for Marketstack API can be found in src/clients/marketstack.py

---
## TimeSeries

## `get_daily`

Sample output (JSON; truncated):

```json
{
  "2025-12-05": {
    "1. open": "280.5400",
    "2. high": "281.1400",
    "3. low": "278.0500",
    "4. close": "278.7800",
    "5. volume": "47265845"
  },
  "2025-12-04": {
    "1. open": "284.0950",
    "2. high": "284.7300",
    "3. low": "278.5900",
    "4. close": "280.7000",
    "5. volume": "43989056"
  },
}
