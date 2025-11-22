# FINNHUB

Here are the functions available under the free-tier API for finnhub. Each section includes the function name and a sample output.

More infos can be found here:  
https://finnhub.io/pricing  

For initialization, please refer:  
https://github.com/Finnhub-Stock-API/finnhub-python

---

## `company_basic_financials`

**Output:**

{"period": "1995-09-30", "v": 1.6259},
{"period": "1995-06-30", "v": 1.6548},
{"period": "1995-03-31", "v": 1.6394},
...

## `company_earnings`

**Output:**

[{'actual': 7.02, 'estimate': 5.7519, 'period': '2025-09-30', 'quarter': 3, 'surprise': 1.2681, 'surprisePercent': 22.0466, 'symbol': 'LLY', 'year': 2025}, {'actual': 6.31, 'estimate': 5.5107, 'period': '2025-06-30', 'quarter': 2, 'surprise': 0.7993, 'surprisePercent': 14.5045, 'symbol': 'LLY', 'year': 2025}
...
]

## `company_news`

**Output:**

[{'category': 'company', 'datetime': 1763158405, 'headline': 'Retail Investors Really Don’t Like Novo Nordisk (NVO) Stock', 'id': 137483679, 'image': 'https://s.yimg.com/rz/stage/p/yahoo_finance_en-US_h_p_finance_2.png', 'related': 'LLY', 'source': 'Yahoo', 'summary': 'Shares of Novo Nordisk A/S (NYSE: NVO) dropped 1.9%today, closing at $48.25, just a whisker above the 52-week low of $45.05. Sometimes we see a divergence in share price and sentiment, but with Novo Nordisk they’re actually well correlated. Discussion on Reddit has remained uniformly bearish throughout November. Novo Nordisk is trading more than 50% ... Retail Investors Really Don’t Like Novo Nordisk (NVO) Stock', 'url': 'https://finnhub.io/api/news?id=9b6d0c0a9bfde34c169302926d97aac5113bdab2113ee4e6650604cc457bcc74'}
  ...
]

## `company_peers`

**Output:**

['LLY', 'JNJ', 'MRK', 'PFE', 'BMY', 'ZTS', 'RPRX', 'VTRS', 'ELAN', 'CORT']

## `company_profile2`

**Output:**

{'country': 'US', 'currency': 'USD', 'estimateCurrency': 'USD', 'exchange': 'NEW YORK STOCK EXCHANGE, INC.', 'finnhubIndustry': 'Pharmaceuticals', 'ipo': '1970-07-09', 'logo': 'https://static2.finnhub.io/file/publicdatany/finnhubimage/stock_logo/LLY.png', 'marketCapitalization': 969283.0240446691, 'name': 'Eli Lilly and Co', 'phone': '13172762000', 'shareOutstanding': 946.46, 'ticker': 'LLY', 'weburl': 'https://www.lilly.com/'}

## `country`

**Output:**

[
    {'code2': 'NR', 'code3': 'NRU', 'codeNo': '520', 'country': 'Nauru', 'countryRiskPremium': None, 'currency': 'Australian Dollars', 'currencyCode': 'AUD', 'defaultSpread': None, 'equityRiskPremium': None, 'rating': None, 'region': 'Oceania', 'subRegion': 'Micronesia'},
...
]

