# FINNHUB

Here are the functions available under the free-tier API for Finnhub. Each section lists the function name and a sample raw output (truncated for brevity).

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
]
```

## `filings`

Sample output (JSON, truncated):

```json
[
  {
    "accessNumber": "0000059478-20-000112",
    "symbol": "LLY",
    "cik": "59478",
    "form": "4",
    "filedDate": "2020-06-09 00:00:00",
    "acceptedDate": "2020-06-09 16:52:54",
    "reportUrl": "https://www.sec.gov/Archives/edgar/data/1596336/000005947820000112/wf-form4_159173595632339.xml",
    "filingUrl": "https://www.sec.gov/Archives/edgar/data/1596336/000005947820000112/0000059478-20-000112-index.html"
  },
]
```

## `financials_reported`

Sample output (JSON, truncated):

```json
[
  {
    "concept": "us-gaap_AccruedIncomeTaxesNoncurrent",
    "unit": "usd",
    "label": "Long-term income taxes payable (Note 14)",
    "value": 3607200000
  },
  {
    "concept": "us-gaap_OtherLiabilitiesNoncurrent",
    "unit": "usd",
    "label": "Other noncurrent liabilities",
    "value": 1014300000
  },
]
```

## `forex_exchanges`

Sample output:

```python
['oanda', 'fxcm', 'forex.com', 'fhfx', 'capital', 'pepperstone', 'fxpig', 'ic markets', 'pepperstoneuk', 'icmtrader', 'deriv']
```

## `forex_symbols`

Sample output (JSON, truncated):

```json
[
  {
    "description": "Oanda EUR/GBP",
    "displaySymbol": "EUR/GBP",
    "symbol": "OANDA:EUR_GBP"
  },
  {
    "description": "Oanda Silver/AUD",
    "displaySymbol": "XAG/AUD",
    "symbol": "OANDA:XAG_AUD"
  },
]
```

## `general_news`

Sample output (JSON, truncated):

```json
[
  {
    "category": "top news",
    "datetime": 1763312400,
    "headline": "The stock market faces big questions about the economy this week. How to be strategic as delayed data comes out.",
    "id": 7555018,
    "image": "https://static2.finnhub.io/file/publicdatany/finnhubimage/market_watch_logo.png",
    "related": "",
    "source": "MarketWatch",
    "summary": "Stock investors may be in for an unsettling start to the week if doubts about the AI trade keep colliding with concerns around the upcoming release of backlogged economic data.",
    "url": "https://www.marketwatch.com/story/the-stock-market-faces-big-questions-about-the-economy-this-week-how-to-be-strategic-as-delayed-data-comes-out-fd7f5e2c"
  },
]
```

## `ipo_calendar`

Sample output (JSON, truncated):

```json
{
  "ipoCalendar": [
    {
      "date": "2025-10-31",
      "exchange": "NYSE",
      "name": "Viking Acquisition Corp I",
      "numberOfShares": 20000000,
      "price": "10.00",
      "status": "priced",
      "symbol": "VACIU",
      "totalSharesValue": 200000000
    },
    {
      "date": "2025-10-31",
      "exchange": "NASDAQ Capital",
      "name": "Nomadar Corp.",
      "numberOfShares": 13268718,
      "price": null,
      "status": "priced",
      "symbol": "NOMA",
      "totalSharesValue": 0
    },
  ]
}
```

## `quote`

Sample output (JSON, truncated):

```json
{
  "c": 1025.28,
  "d": 2.41,
  "dp": 0.2356,
  "h": 1033.6185,
  "l": 1007.785,
  "o": 1009,
  "pc": 1022.87,
  "t": 1763154000
}
```

## `recommendation_trends`

Sample output (JSON, truncated):

```json
[
  {
    "buy": 18,
    "hold": 9,
    "period": "2025-11-01",
    "sell": 0,
    "strongBuy": 9,
    "strongSell": 0,
    "symbol": "LLY"
  },
  {
    "buy": 17,
    "hold": 9,
    "period": "2025-10-01",
    "sell": 0,
    "strongBuy": 9,
    "strongSell": 0,
    "symbol": "LLY"
  },
]
```

## `stock_insider_sentiment`

Sample output (JSON, truncated):

```json
{
  "data": [
    {
      "symbol": "LLY",
      "year": 2022,
      "month": 1,
      "change": 216,
      "mspr": 100
    },
    {
      "symbol": "LLY",
      "year": 2022,
      "month": 2,
      "change": 204501,
      "mspr": 66.54096
    },
  ],
}
```

## `stock_insider_transactions`

Sample output (JSON, truncated):

```json
{
  "data": [
    {
      "change": -800,
      "currency": "",
      "filingDate": "2025-10-02",
      "id": "0000316011-25-000019",
      "isDerivative": false,
      "name": "LILLY ENDOWMENT INC",
      "share": 95141978,
      "source": "sec",
      "symbol": "LLY",
      "transactionCode": "S",
      "transactionDate": "2025-10-01",
      "transactionPrice": 833.154
    },
    {
      "change": -5668,
      "currency": "",
      "filingDate": "2025-10-02",
      "id": "0000316011-25-000019",
      "isDerivative": false,
      "name": "LILLY ENDOWMENT INC",
      "share": 95142778,
      "source": "sec",
      "symbol": "LLY",
      "transactionCode": "S",
      "transactionDate": "2025-10-01",
      "transactionPrice": 832.432
    },
  ]
}
```

## `stock_lobbying`

Sample output (JSON, truncated):

```json
{
  "data": [
    {
      "symbol": "LLY",
      "name": "ELI LILLY AND COMPANY",
      "description": "American pharmaceutical company.",
      "country": "US",
      "year": 2025,
      "period": "Q3",
      "documentUrl": "https://lda.senate.gov/filings/public/filing/9c1f4d73-d535-4b0e-b3e6-7ce357333eb9/print/",
      "income": 80000,
      "expenses": null,
      "postedName": "",
      "date": "",
      "clientId": "55430",
      "registrantId": "401103321",
      "senateId": "401103321-55430",
      "houseRegistrantId": "401103321"
    },
    {
      "symbol": "LLY",
      "name": "ELI LILLY AND COMPANY",
      "description": "Biopharmaceutical company",
      "country": "US",
      "year": 2025,
      "period": "Q3",
      "documentUrl": "https://lda.senate.gov/filings/public/filing/8a340ca3-b194-4113-9bff-902774301f85/print/",
      "income": 60000,
      "expenses": null,
      "postedName": "",
      "date": "",
      "clientId": "63502",
      "registrantId": "401106573",
      "senateId": "401106573-63502",
      "houseRegistrantId": ""
    },
  ],
}
```

## `stock_usa_spending`

Sample output (JSON, truncated):

```json
{
  "data": [
    {
      "symbol": "LLY",
      "recipientName": "ELI LILLY AND COMPANY",
      "recipientParentName": "ELI LILLY AND COMPANY",
      "country": "USA",
      "totalValue": 0,
      "outlayedAmount": 0,
      "obligatedAmount": 0,
      "potentialAmount": 3600000000,
      "actionDate": "2024-09-13",
      "performanceStartDate": "2018-08-01",
      "performanceEndDate": "",
      "awardingAgencyName": "Department of Veterans Affairs",
      "awardingSubAgencyName": "Department of Veterans Affairs",
      "awardingOfficeName": "NAC FEDERAL SUPPLY SCHEDULE (36F797)",
      "performanceCountry": "",
      "performanceCity": "",
      "performanceCounty": "",
      "performanceState": "",
      "performanceZipCode": "",
      "performanceCongressionalDistrict": "IN-07",
      "awardDescription": "65 I B, DRUGS, PHARMACEUTICALS,&HEMATOLOGY RELATED PRODUCTS, FSS CONTRACT AWARD",
      "naicsCode": "325412",
      "permalink": "https://www.usaspending.gov/award/CONT_IDV_36F79718D0503_3600/",
      "lastModifiedDate": "2024-09-13"
    },
    {
      "symbol": "LLY",
      "recipientName": "ELI LILLY AND COMPANY",
      "recipientParentName": "ELI LILLY AND COMPANY",
      "country": "USA",
      "totalValue": 0,
      "outlayedAmount": 0,
      "obligatedAmount": 0,
      "potentialAmount": 3600000000,
      "actionDate": "2024-09-13",
      "performanceStartDate": "2018-08-01",
      "performanceEndDate": "",
      "awardingAgencyName": "Department of Veterans Affairs",
      "awardingSubAgencyName": "Department of Veterans Affairs",
      "awardingOfficeName": "NAC FEDERAL SUPPLY SCHEDULE (36F797)",
      "performanceCountry": "",
      "performanceCity": "",
      "performanceCounty": "",
      "performanceState": "",
      "performanceZipCode": "",
      "performanceCongressionalDistrict": "IN-07",
      "awardDescription": "65 I B, DRUGS, PHARMACEUTICALS,&HEMATOLOGY RELATED PRODUCTS, FSS CONTRACT AWARD",
      "naicsCode": "325412",
      "permalink": "https://www.usaspending.gov/award/CONT_IDV_36F79718D0503_3600/",
      "lastModifiedDate": "2024-09-13"
    }
  ]
}
```

## `stock_uspto_patent`

Sample output (JSON, truncated):

```json
{
  "data": [
    {
      "applicationNumber": "18675439",
      "companyFilingName": ["ELI LILLY AND COMPANY"],
      "description": "POLYMORPHS OF AN SSAO INHIBITOR",
      "filingDate": "2024-05-28 00:00:00",
      "filingStatus": "Application",
      "patentNumber": "US20240308975A1",
      "patentType": "Utility",
      "publicationDate": "2024-09-19 00:00:00",
      "url": ""
    },
    {
      "applicationNumber": "18673584",
      "companyFilingName": ["ELI LILLY AND COMPANY"],
      "description": "ANTIBODIES TARGETING XCL1 AND METHODS OF USING THE SAME",
      "filingDate": "2024-05-24 00:00:00",
      "filingStatus": "Application",
      "patentNumber": "US20240391992A1",
      "patentType": "Utility",
      "publicationDate": "2024-11-28 00:00:00",
      "url": ""
    },
  ]
}
```

## `stock_visa_application`

Sample output (JSON, truncated):

```json
{
  "data": [
    {
      "year": 2024,
      "quarter": 1,
      "symbol": "LLY",
      "caseNumber": "I-200-24040-708313",
      "caseStatus": "Certified",
      "receivedDate": "2024-02-09",
      "visaClass": "H-1B",
      "jobTitle": "Sr IT Manufacturing Execution Systems Business Integrator",
      "socCode": "17-2112.03",
      "fullTimePosition": "Y",
      "beginDate": "2024-02-13",
      "endDate": "2027-02-12",
      "employerName": "Eli Lilly and Company",
      "worksiteAddress": "1555 S Harding Street",
      "worksiteCity": "Indianapolis",
      "worksiteCounty": "MARION",
      "worksiteState": "IN",
      "worksitePostalCode": "46221",
      "wageRangeFrom": 102000,
      "wageRangeTo": null,
      "wageUnitOfPay": "Year",
      "wageLevel": "III",
      "h1bDependent": "No"
    },
    {
      "year": 2024,
      "quarter": 1,
      "symbol": "LLY",
      "caseNumber": "I-200-24018-647756",
      "caseStatus": "Certified",
      "receivedDate": "2024-01-17",
      "visaClass": "H-1B",
      "jobTitle": "Sr. Scientist - TS/MS Validation",
      "socCode": "17-2112.02",
      "fullTimePosition": "Y",
      "beginDate": "2024-01-19",
      "endDate": "2027-01-18",
      "employerName": "Eli Lilly and Company",
      "worksiteAddress": "1555 S Harding Street",
      "worksiteCity": "Indianapolis",
      "worksiteCounty": "MARION",
      "worksiteState": "IN",
      "worksitePostalCode": "46221",
      "wageRangeFrom": 100000,
      "wageRangeTo": null,
      "wageUnitOfPay": "Year",
      "wageLevel": "III",
      "h1bDependent": "No"
    },
  ],
}
```

## `symbol_lookup`

Sample output (JSON, truncated):

```json
{
  "count": 14,
  "result": [
    {
      "description": "ELI LILLY & CO",
      "displaySymbol": "LLY",
      "symbol": "LLY",
      "type": "Common Stock"
    },
    {
      "description": "ELI LILLY & CO-CDR",
      "displaySymbol": "LLY.NE",
      "symbol": "LLY.NE",
      "type": "Canadian DR"
    },
  ]
}
```
---

Notes:

- All samples are truncated for brevity. Use the official Finnhub endpoints to retrieve full results.
- Values and timestamps in these examples are illustrative and may change over time.

