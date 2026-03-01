# Data Providers

## Overview
The `data_providers` module contains Python wrappers for various APIs. These wrappers normalize responses into JSON-friendly formats and add metadata such as provider name, endpoint, timestamp, and ticker.

## Implemented Providers
- **Alphavantage**: Financial data.
- **Finnhub**: Stock market data.
- **FRED**: Macroeconomic data.
- **SEC Edgar**: Regulatory filings.
- **OpenFDA**: FDA data.
- **Marketstack**: Market data.
- **Massive**: General data.

## Directory Structure
```
src/data_providers/
├── alphavintage.py
├── base.py
├── finnhub.py
├── fred.py
├── marketstack.py
├── massive.py
├── openfda.py
├── sec_edgar.py
└── __init__.py
```