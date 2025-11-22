# FINNHUB

Here are the functions available under the free-tier API for Finnhub. Each section lists the function name and a sample output (truncated for brevity).

More info: https://finnhub.io/pricing

For initialization, see the `finnhub-python` client: https://github.com/Finnhub-Stock-API/finnhub-python

---

## `company_basic_financials`

Sample output (JSON; truncated):

```json
[
  {"period": "1995-09-30", "v": 1.6259},
  {"period": "1995-06-30", "v": 1.6548},
  {"period": "1995-03-31", "v": 1.6394}
]
```

## `company_earnings`

Sample output (JSON; truncated):

```json
[
  {
    "actual": 7.02,
    "estimate": 5.7519,
    "period": "2025-09-30",
    "quarter": 3,
    "surprise": 1.2681,
    "surprisePercent": 22.0466,
    "symbol": "LLY",
    "year": 2025
  },
  {
    "actual": 6.31,
    "estimate": 5.5107,
    "period": "2025-06-30",
    "quarter": 2,
    "surprise": 0.7993,
    "surprisePercent": 14.5045,
    "symbol": "LLY",
    "year": 2025
  }
]
```

## `company_news`

Sample output (JSON; truncated):

```json
[
  {
    "category": "company",
    "datetime": 1763158405,
    "headline": "Retail Investors Really Don’t Like Novo Nordisk (NVO) Stock",
    "id": 137483679,
    "image": "https://s.yimg.com/rz/stage/p/yahoo_finance_en-US_h_p_finance_2.png",
    "related": "LLY",
    "source": "Yahoo",
    "summary": "Shares of Novo Nordisk A/S (NYSE: NVO) dropped 1.9% today...",
    "url": "https://finnhub.io/api/news?id=..."
  }
]
```

## `company_peers`

Sample output (JSON):

```json
["LLY", "JNJ", "MRK", "PFE", "BMY", "ZTS", "RPRX", "VTRS", "ELAN", "CORT"]
```

## `company_profile2`

Sample output (JSON):

```json
{
  "country": "US",
  "currency": "USD",
  "estimateCurrency": "USD",
  "exchange": "NEW YORK STOCK EXCHANGE, INC.",
  "finnhubIndustry": "Pharmaceuticals",
  "ipo": "1970-07-09",
  "logo": "https://static2.finnhub.io/file/publicdatany/finnhubimage/stock_logo/LLY.png",
  "marketCapitalization": 969283.0240446691,
  "name": "Eli Lilly and Co",
  "phone": "13172762000",
  "shareOutstanding": 946.46,
  "ticker": "LLY",
  "weburl": "https://www.lilly.com/"
}
```

## `country`

Sample output (JSON; truncated):

```json
[
  {
    "code2": "NR",
    "code3": "NRU",
    "codeNo": "520",
    "country": "Nauru",
    "countryRiskPremium": null,
    "currency": "Australian Dollars",
    "currencyCode": "AUD",
    "defaultSpread": null,
    "equityRiskPremium": null,
    "rating": null,
    "region": "Oceania",
    "subRegion": "Micronesia"
  }
]
```

## `covid19`

Sample output (JSON; truncated):

```json
[
  {
    "state": "California", 
    "case": 12711918, 
    "death": 112443, 
    "updated": "2024-11-18 18:02:03"},
]
```

## `crypto_exchanges`

Sample output (JSON):

```json
["BINANCE", "POLONIEX", "OKEX", "BINANCEUS", "COINBASE", "GEMINI", "HUOBI", "KRAKEN", "HITBTC", "KUCOIN", "BITFINEX", "BITMEX"]
```

## `crypto_symbols`

Sample output (JSON; truncated):

```json
[
  {
    "description": "Binance LINA/USDT",
    "displaySymbol": "LINA/USDT",
    "symbol": "BINANCE:LINAUSDT"
  },
  {
    "description": "Binance ARKM/USDC",
    "displaySymbol": "ARKM/USDC",
    "symbol": "BINANCE:ARKMUSDC"
  },
]
```

## `earnings_calender`

Sample output (JSON):

```json
{"earningsCalendar": []}
```

## `fda_calendar`

Sample output (JSON; truncated):

```json
[
  {
    "fromDate": "2025-12-03 09:00:00",
    "toDate": "2025-12-03 18:00:00",
    "eventDescription": "December 3, 2025: Circulatory System Devices Panel Advisory Committee Meeting Announcement - 12/03/2025",
    "url": "https://www.fda.gov/advisory-committees/advisory-committee-calendar/december-3-2025-circulatory-system-devices-panel-advisory-committee-meeting-announcement-12032025"
  },
  {
    "fromDate": "2025-11-13 10:00:00",
    "toDate": "2025-11-13 16:00:00",
    "eventDescription": "Pediatric Advisory Committee Meeting Announcement - 11/13/2025",
    "url": "https://www.fda.gov/advisory-committees/advisory-committee-calendar/pediatric-advisory-committee-meeting-announcement-11132025"
  },
]
```
---

Notes:

- All samples are truncated for brevity. Use the official Finnhub endpoints to retrieve full results.
- Values and timestamps in these examples are illustrative and may change over time.

