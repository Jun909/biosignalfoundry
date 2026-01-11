# MARKETSTACK

Here are the functions available under the free-tier API for Marketstack. Each section lists the function name and a sample output (truncated for brevity).

More info: https://marketstack.com/pricing

For API documentation, check: https://marketstack.com/documentation_v2

A simple python wrapper for Marketstack API can be found in src/data_providers/marketstack.py

---

## `eod_data`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 100,
    "total": 249
  },
  "data": [
    {
      "open": 274.16,
      "high": 275.37,
      "low": 272.86,
      "close": 273.4,
      "volume": 21521802.0,
      "adj_high": 275.37,
      "adj_low": 272.86,
      "adj_close": 273.4,
      "adj_open": 274.16,
      "adj_volume": 21521802.0,
      "split_factor": 1.0,
      "dividend": 0.0,
      "name": "Apple Inc",
      "exchange_code": "NASDAQ",
      "asset_type": "Stock",
      "price_currency": "USD",
      "symbol": "AAPL",
      "exchange": "XNAS",
      "date": "2025-12-26T00:00:00+0000"
    },
    {
      "open": 272.34,
      "high": 275.43,
      "low": 272.2,
      "close": 273.81,
      "volume": 17910600.0,
      "adj_high": 275.43,
      "adj_low": 272.195,
      "adj_close": 273.81,
      "adj_open": 272.34,
      "adj_volume": 17910574.0,
      "split_factor": 1.0,
      "dividend": 0.0,
      "name": "Apple Inc",
      "exchange_code": "NASDAQ",
      "asset_type": "Stock",
      "price_currency": "USD",
      "symbol": "AAPL",
      "exchange": "XNAS",
      "date": "2025-12-24T00:00:00+0000"
    }
  ]
}

```

## `eod_latest_data`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 1,
    "total": 1
  },
  "data": [
    {
      "open": 274.16,
      "high": 275.37,
      "low": 272.86,
      "close": 273.4,
      "volume": 21521802.0,
      "adj_high": 275.37,
      "adj_low": 272.86,
      "adj_close": 273.4,
      "adj_open": 274.16,
      "adj_volume": 21521802.0,
      "split_factor": 1.0,
      "dividend": 0.0,
      "name": "Apple Inc",
      "exchange_code": "NASDAQ",
      "asset_type": "Stock",
      "price_currency": "USD",
      "symbol": "AAPL",
      "exchange": "XNAS",
      "date": "2025-12-26T00:00:00+0000"
    }
  ]
}

```

## `eod_data_specific_date`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 1,
    "total": 1
  },
  "data": [
    {
      "open": 286.2,
      "high": 288.61,
      "low": 283.54,
      "close": 284.15,
      "volume": 38438153.0,
      "adj_high": 288.62,
      "adj_low": 283.3,
      "adj_close": 284.15,
      "adj_open": 286.2,
      "adj_volume": 43538687.0,
      "split_factor": 1.0,
      "dividend": 0.0,
      "name": "Apple Inc",
      "exchange_code": "NASDAQ",
      "asset_type": "Stock",
      "price_currency": "USD",
      "symbol": "AAPL",
      "exchange": "XNAS",
      "date": "2025-12-03T00:00:00+0000"
    }
  ]
}

```
## `splits_data`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 5,
    "total": 5
  },
  "data": [
    {
      "date": "2020-08-31",
      "split_factor": 4.0,
      "stock_split": null,
      "symbol": "AAPL"
    },
    {
      "date": "2014-06-09",
      "split_factor": 7.0,
      "stock_split": null,
      "symbol": "AAPL"
    },
  ]
}

```
## `dividends_data`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 90,
    "total": 90
  },
  "data": [
    {
      "date": "2025-11-10",
      "dividend": 0.26,
      "payment_date": "2025-11-13 05:00:00",
      "record_date": "2025-11-10 05:00:00",
      "declaration_date": "2025-10-30 00:00:00",
      "distr_freq": "q",
      "symbol": "AAPL"
    },
    {
      "date": "2025-08-11",
      "dividend": 0.26,
      "payment_date": "2025-08-14 04:00:00",
      "record_date": "2025-08-11 04:00:00",
      "declaration_date": "2025-07-31 00:00:00",
      "distr_freq": "q",
      "symbol": "AAPL"
    },
  ]
}

```
## `ticker_information`

Sample output (JSON; truncated):

```json
{
  "name": "Apple Inc.",
  "symbol": "AAPL",
  "cik": "320193",
  "isin": "US0378331005",
  "cusip": "037833100",
  "ein_employer_id": "942404110",
  "lei": "HWUPKR0MPOU8FGXBT394",
  "series_id": "",
  "item_type": "equity",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "sic_code": "3571",
  "sic_name": "Electronic Computers",
  "stock_exchange": {
    "name": "NASDAQ - ALL MARKETS",
    "acronym": "NASDAQ",
    "mic": "XNAS",
    "country": null,
    "country_code": "US",
    "city": "NEW YORK",
    "website": "WWW.NASDAQ.COM",
    "operating_mic": "XNAS",
    "oprt_sgmt": "OPRT",
    "legal_entity_name": "",
    "exchange_lei": "",
    "market_category_code": "NSPD",
    "exchange_status": "ACTIVE",
    "date_creation": {
      "date": "2005-06-27 00:00:00.000000",
      "timezone_type": 1,
      "timezone": "+00:00"
    },
    "date_last_update": {
      "date": "2005-06-27 00:00:00.000000",
      "timezone_type": 1,
      "timezone": "+00:00"
    },
    "date_last_validation": null,
    "date_expiry": null,
    "comments": ""
  }
}

```
## `eod_data_specific_ticker`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 100,
    "total": 249
  },
  "data": {
    "name": "Apple Inc",
    "symbol": "AAPL",
    "has_intraday": false,
    "has_eod": true,
    "country": null,
    "eod": [
      {
        "open": 274.16,
        "high": 275.37,
        "low": 272.86,
        "close": 273.4,
        "volume": 21455300.0,
        "adj_high": 275.37,
        "adj_low": 272.86,
        "adj_close": 273.4,
        "adj_open": 274.16,
        "adj_volume": 21521802.0,
        "split_factor": 1.0,
        "dividend": 0.0,
        "name": "Apple Inc",
        "exchange_code": "NASDAQ",
        "asset_type": "Stock",
        "price_currency": "USD",
        "symbol": "AAPL",
        "exchange": "XNAS",
        "date": "2025-12-26T00:00:00+0000"
      }
    ]
  }
}

```
## `splits_factor_specific_ticker`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 5,
    "total": 5
  },
  "data": [
    {
      "date": "2020-08-31",
      "split_factor": 4.0,
      "stock_split": null,
      "symbol": "AAPL"
    },
    {
      "date": "2014-06-09",
      "split_factor": 7.0,
      "stock_split": null,
      "symbol": "AAPL"
    },
  ]
}

```
## `dividends_data_specific_ticker`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 90,
    "total": 90
  },
  "data": [
    {
      "date": "2025-11-10",
      "dividend": 0.26,
      "payment_date": "2025-11-13 05:00:00",
      "record_date": "2025-11-10 05:00:00",
      "declaration_date": "2025-10-30 00:00:00",
      "distr_freq": "q",
      "symbol": "AAPL"
    },
    {
      "date": "2025-08-11",
      "dividend": 0.26,
      "payment_date": "2025-08-14 04:00:00",
      "record_date": "2025-08-11 04:00:00",
      "declaration_date": "2025-07-31 00:00:00",
      "distr_freq": "q",
      "symbol": "AAPL"
    },
  ]
}

```
## `eod_specific_ticker_specific_date`

Sample output (JSON; truncated):

```json
{
  "open": 286.2,
  "high": 288.61,
  "low": 283.54,
  "close": 284.15,
  "volume": 38438153.0,
  "adj_high": 288.62,
  "adj_low": 283.3,
  "adj_close": 284.15,
  "adj_open": 286.2,
  "adj_volume": 43538687.0,
  "split_factor": 1.0,
  "dividend": 0.0,
  "name": "Apple Inc",
  "exchange_code": "NASDAQ",
  "asset_type": "Stock",
  "price_currency": "USD",
  "symbol": "AAPL",
  "exchange": "XNAS",
  "date": "2025-12-03T00:00:00+0000"
}

```
## `eod_latest_data_specific_ticker`

Sample output (JSON; truncated):

```json
{
  "open": 274.16,
  "high": 275.37,
  "low": 272.86,
  "close": 273.4,
  "volume": 21521802.0,
  "adj_high": 275.37,
  "adj_low": 272.86,
  "adj_close": 273.4,
  "adj_open": 274.16,
  "adj_volume": 21521802.0,
  "split_factor": 1.0,
  "dividend": 0.0,
  "name": "Apple Inc",
  "exchange_code": "NASDAQ",
  "asset_type": "Stock",
  "price_currency": "USD",
  "symbol": "AAPL",
  "exchange": "XNAS",
  "date": "2025-12-26T00:00:00+0000"
}

```
## `tickers_list`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 100,
    "total": 668499
  },
  "data": [
    {
      "name": "Microsoft Corporation",
      "ticker": "MSFT",
      "has_intraday": false,
      "has_eod": true,
      "stock_exchange": {
        "name": "NASDAQ - ALL MARKETS",
        "acronym": "NASDAQ",
        "mic": "XNAS"
      }
    },
    {
      "name": "Apple Inc",
      "ticker": "AAPL",
      "has_intraday": false,
      "has_eod": true,
      "stock_exchange": {
        "name": "NASDAQ - ALL MARKETS",
        "acronym": "NASDAQ",
        "mic": "XNAS"
      }
    }
  ]
}

```
## `exchanges`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 100,
    "total": 2809
  },
  "data": [
    {
      "name": "NASDAQ - ALL MARKETS",
      "acronym": "NASDAQ",
      "mic": "XNAS",
      "country": null,
      "country_code": "US",
      "city": "NEW YORK",
      "website": "www.nasdaq.com",
      "operating_mic": "XNAS",
      "oprt_sgmt": "OPRT",
      "legal_entity_name": "",
      "exchange_lei": "",
      "market_category_code": "NSPD",
      "exchange_status": "ACTIVE",
      "date_creation": "2005-06-27",
      "date_last_update": "2005-06-27",
      "date_last_validation": null,
      "date_expiry": null,
      "comments": ""
    }
  ]
}

```
## `specific_stock_exchange_info`

Sample output (JSON; truncated):

```json
{
  "data": {
    "name": "NASDAQ - ALL MARKETS",
    "acronym": "NASDAQ",
    "mic": "XNAS",
    "country": null,
    "country_code": "US",
    "city": "NEW YORK",
    "website": "WWW.NASDAQ.COM",
    "operating_mic": "XNAS",
    "oprt_sgmt": "OPRT",
    "legal_entity_name": "",
    "exchange_lei": "",
    "market_category_code": "NSPD",
    "exchange_status": "ACTIVE",
    "date_creation": "2005-06-27",
    "date_last_update": "2005-06-27",
    "date_last_validation": null,
    "date_expiry": null,
    "comments": ""
  }
}

```
## `specific_stock_exchange_ticker`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 100,
    "total": 45020
  },
  "data": {
    "name": "NASDAQ - ALL MARKETS",
    "acronym": "NASDAQ",
    "mic": "XNAS",
    "country": null,
    "city": "NEW YORK",
    "website": "WWW.NASDAQ.COM",
    "operating_mic": "XNAS",
    "oprt_sgmt": "OPRT",
    "legal_entity_name": "",
    "exchange_lei": "",
    "market_category_code": "NSPD",
    "exchange_status": "ACTIVE",
    "date_creation": "2005-06-27",
    "date_last_update": "2005-06-27",
    "date_last_validation": null,
    "date_expiry": null,
    "comments": "",
    "tickers": [
      {
        "name": "Microsoft Corporation",
        "symbol": "MSFT",
        "has_intraday": false,
        "has_eod": true
      },
      {
        "name": "Apple Inc",
        "symbol": "AAPL",
        "has_intraday": false,
        "has_eod": true
      }
    ]
  }
}

```
## `eod_data_specific_stock_exchange`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 100,
    "total": 249
  },
  "data": {
    "name": "NASDAQ - ALL MARKETS",
    "acronym": "NASDAQ",
    "mic": "XNAS",
    "country": null,
    "city": "NEW YORK",
    "website": "WWW.NASDAQ.COM",
    "operating_mic": "XNAS",
    "oprt_sgmt": "OPRT",
    "legal_entity_name": "",
    "exchange_lei": "",
    "market_category_code": "NSPD",
    "exchange_status": "ACTIVE",
    "date_creation": "2005-06-27",
    "date_last_update": "2005-06-27",
    "date_last_validation": null,
    "date_expiry": null,
    "comments": "",
    "eod": [
      {
        "open": 274.16,
        "high": 275.37,
        "low": 272.86,
        "close": 273.4,
        "volume": 21455300.0,
        "adj_high": 275.37,
        "adj_low": 272.86,
        "adj_close": 273.4,
        "adj_open": 274.16,
        "adj_volume": 21521802.0,
        "split_factor": 1.0,
        "dividend": 0.0,
        "name": "Apple Inc",
        "exchange_code": "NASDAQ",
        "asset_type": "Stock",
        "price_currency": "USD",
        "symbol": "AAPL",
        "exchange": "XNAS",
        "date": "2025-12-26T00:00:00+0000"
      }
    ]
  }
}

```
## `eod_data_latest_date_specific_stock_exchange`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 1,
    "total": 1
  },
  "data": {
    "name": "NASDAQ - ALL MARKETS",
    "acronym": "NASDAQ",
    "mic": "XNAS",
    "country": null,
    "city": "NEW YORK",
    "website": "WWW.NASDAQ.COM",
    "operating_mic": "XNAS",
    "oprt_sgmt": "OPRT",
    "legal_entity_name": "",
    "exchange_lei": "",
    "market_category_code": "NSPD",
    "exchange_status": "ACTIVE",
    "date_creation": "2005-06-27",
    "date_last_update": "2005-06-27",
    "date_last_validation": null,
    "date_expiry": null,
    "comments": "",
    "eod": [
      {
        "open": 274.16,
        "high": 275.37,
        "low": 272.86,
        "close": 273.4,
        "volume": 21455300.0,
        "adj_high": 275.37,
        "adj_low": 272.86,
        "adj_close": 273.4,
        "adj_open": 274.16,
        "adj_volume": 21521802.0,
        "split_factor": 1.0,
        "dividend": 0.0,
        "name": "Apple Inc",
        "exchange_code": "NASDAQ",
        "asset_type": "Stock",
        "price_currency": "USD",
        "symbol": "AAPL",
        "exchange": "XNAS",
        "date": "2025-12-26T00:00:00+0000"
      }
    ]
  }
}

```
## `eod_data_specific_stock_exchange_specific_date`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 1,
    "total": 1
  },
  "data": {
    "name": "NASDAQ - ALL MARKETS",
    "acronym": "NASDAQ",
    "mic": "XNAS",
    "country": null,
    "city": "NEW YORK",
    "website": "WWW.NASDAQ.COM",
    "operating_mic": "XNAS",
    "oprt_sgmt": "OPRT",
    "legal_entity_name": "",
    "exchange_lei": "",
    "market_category_code": "NSPD",
    "exchange_status": "ACTIVE",
    "date_creation": "2005-06-27",
    "date_last_update": "2005-06-27",
    "date_last_validation": null,
    "date_expiry": null,
    "comments": "",
    "eod": [
      {
        "open": 286.2,
        "high": 288.61,
        "low": 283.54,
        "close": 284.15,
        "volume": 38438153.0,
        "adj_high": 288.62,
        "adj_low": 283.3,
        "adj_close": 284.15,
        "adj_open": 286.2,
        "adj_volume": 43538687.0,
        "split_factor": 1.0,
        "dividend": 0.0,
        "name": "Apple Inc",
        "exchange_code": "NASDAQ",
        "asset_type": "Stock",
        "price_currency": "USD",
        "symbol": "AAPL",
        "exchange": "XNAS",
        "date": "2025-12-03T00:00:00+0000"
      }
    ]
  }
}

```
## `currencies`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 43,
    "total": 43
  },
  "data": [
    {
      "code": "USD",
      "symbol": "$",
      "name": "US Dollar"
    },
    {
      "code": "ARS",
      "symbol": "AR$",
      "name": "Argentine Peso"
    },
    {
      "code": "EUR",
      "symbol": "€",
      "name": "Euro"
    },
    {
      "code": "BHD",
      "symbol": "BD",
      "name": "Bahraini Dinar"
    },
    {
      "code": "BRL",
      "symbol": "R$",
      "name": "Brazilian Real"
    },
    {
      "code": "CAD",
      "symbol": "CA$",
      "name": "Canadian Dollar"
    }
  ]
}

```
## `timezones`

Sample output (JSON; truncated):

```json
{
  "pagination": {
    "limit": 100,
    "offset": 0,
    "count": 43,
    "total": 43
  },
  "data": [
    {
      "code": "USD",
      "symbol": "$",
      "name": "US Dollar"
    },
    {
      "code": "ARS",
      "symbol": "AR$",
      "name": "Argentine Peso"
    },
    {
      "code": "EUR",
      "symbol": "€",
      "name": "Euro"
    }
  ]
}

```