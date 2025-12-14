# MASSIVE

Here are the functions available under the free-tier API for Massive. Each section lists the function name and a sample raw output (truncated for brevity).

More info: https://massive.com/dashboard/subscriptions?assetClass=stocks&license=personal

For initialization, see: https://github.com/massive-com/client-python

---

## `get_aggs`

Sample output (JSON; truncated):

```json
[
    {
        "open": 705.335,
        "high": 711.96,
        "low": 696.34,
        "close": 700.42,
        "volume": 1116282.0,
        "vwap": 703.3106,
        "timestamp": 1735794000000.0,
        "transactions": 53936.0,
        "otc": null
    },
    {
        "open": 703.16,
        "high": 717.57,
        "low": 702.58,
        "close": 714.36,
        "volume": 1064105.0,
        "vwap": 711.5711,
        "timestamp": 1735880400000.0,
        "transactions": 48407.0,
        "otc": null
    },
]
```

## `get_daily_open_close_agg`

Sample output:

```python
DailyOpenCloseAgg(after_hours=1012, close=1006.98, from_='2025-11-14', high=1018.07, low=981, open=989.3, pre_market=1001.72, status='OK', symbol='ASML', volume=1308114.0, otc=None)
```

## `get_ema`

Sample output (truncated):

```python
SingleIndicatorResults(values=[IndicatorValue(timestamp=1763096400000, value=974.0856848870808), IndicatorValue(timestamp=1763010000000, value=972.7430597804309), IndicatorValue(timestamp=1762923600000, value=970.8199193633056), IndicatorValue(timestamp=1762837200000, value=968.105222194461), IndicatorValue(timestamp=1762750800000, value=965.8882924881125), IndicatorValue(timestamp=1762491600000, value=962.9127125896681), IndicatorValue(timestamp=1762405200000, value=960.7067008586341), IndicatorValue(timestamp=1762318800000, value=957.9110559957212), IndicatorValue(timestamp=1762232400000, value=954.4074256281997), IndicatorValue(timestamp=1762146000000, value=951.3163001436365)], underlying=IndicatorUnderlying(url='https://api.polygon.io/v2/aggs/ticker/ASML/range/1/day/1063281600000/1763219110715?limit=235&sort=desc', aggregates=[]))
```

## `get_exchanges`

Sample output (truncated):

```python
[Exchange(acronym='AMEX', asset_class='stocks', id=1, locale='us', mic='XASE', name='NYSE American, LLC', operating_mic='XNYS', participant_id='A', type='exchange', url='https://www.nyse.com/markets/nyse-american'),] …
```

## `get_macd`

Sample output (truncated):

```python
MACDIndicatorResults(values=[MACDIndicatorValue(timestamp=1763096400000, value=11.327033077914052, signal=20.679499931433593, histogram=-9.352466853519541), MACDIndicatorValue(timestamp=1763010000000, value=14.505302759005417, signal=23.017616644813476, histogram=-8.512313885808059)])
...
```

## `get_market_holidays`

Sample output (truncated):

```python
[MarketHoliday(close=None, date='2025-11-27', exchange='NASDAQ', name='Thanksgiving', open=None, status='closed'), MarketHoliday(close=None, date='2025-11-27', exchange='NYSE', name='Thanksgiving', open=None, status='closed'),]…
```

## `get_market_status`

Sample output (truncated):

```python
MarketStatus(after_hours=False, currencies=MarketCurrencies(crypto='open', fx='closed'), early_hours=False, exchanges=MarketExchanges(nasdaq='closed', nyse='closed', otc='closed'), indicesGroups=MarketIndices(s_and_p='closed', societe_generale='closed', cgi='closed', msci='closed', ftse_russell='closed', mstar='closed', mstarc='closed', cccy='open', nasdaq='closed', dow_jones='closed'), market='closed', server_time='2025-11-15T12:57:46-05:00')
```

## `get_previous_close_agg`

Sample output:

```python
[PreviousCloseAgg(ticker='ASML', close=1006.98, high=1018.07, low=981, open=989.3, timestamp=1763154000000, volume=1308114.0, vwap=1004.7255)]
```

## `get_related_companies(ticker=”PFE”)`

Sample output:

```python
[RelatedCompany(ticker='MRNA'), RelatedCompany(ticker='MRK'), RelatedCompany(ticker='JNJ'), RelatedCompany(ticker='NVAX'), RelatedCompany(ticker='LLY'), RelatedCompany(ticker='ABBV'), RelatedCompany(ticker='BMY'), RelatedCompany(ticker='AMGN'), RelatedCompany(ticker='GILD'), RelatedCompany(ticker='VTRS')]
```

## `get_rsi`

Sample output:

```python
SingleIndicatorResults(values=[IndicatorValue(timestamp=1763096400000, value=51.981751592544214), IndicatorValue(timestamp=1763010000000, value=62.009182403516945), IndicatorValue(timestamp=1762923600000, value=63.25079816865726), IndicatorValue(timestamp=1762837200000, value=59.895322686556305), IndicatorValue(timestamp=1762750800000, value=45.526450921460686), IndicatorValue(timestamp=1762491600000, value=46.07389511940083), IndicatorValue(timestamp=1762405200000, value=52.19308045623744), IndicatorValue(timestamp=1762318800000, value=48.56861320009467), IndicatorValue(timestamp=1762232400000, value=43.42401694005906), IndicatorValue(timestamp=1762146000000, value=48.674248271752866)], underlying=IndicatorUnderlying(url='https://api.polygon.io/v2/aggs/ticker/PFE/range/1/day/1063281600000/1763233976848?limit=75&sort=desc', aggregates=[]))
```

## `get_sma`

Sample output:

```python
SingleIndicatorResults(values=[IndicatorValue(timestamp=1763096400000, value=24.794199999999996), IndicatorValue(timestamp=1763010000000, value=24.790599999999998), IndicatorValue(timestamp=1762923600000, value=24.7656), IndicatorValue(timestamp=1762837200000, value=24.744), IndicatorValue(timestamp=1762750800000, value=24.733400000000003), IndicatorValue(timestamp=1762491600000, value=24.7408), IndicatorValue(timestamp=1762405200000, value=24.744199999999996), IndicatorValue(timestamp=1762318800000, value=24.748599999999996), IndicatorValue(timestamp=1762232400000, value=24.7548), IndicatorValue(timestamp=1762146000000, value=24.771600000000003)], underlying=IndicatorUnderlying(url='https://api.polygon.io/v2/aggs/ticker/PFE/range/1/day/1063281600000/1763234003317?limit=235&sort=desc', aggregates=[]))
```

## `get_ticker_details`

Sample output:

```python
TickerDetails(active=True, address=CompanyAddress(address1='LILLY CORPORATE CTR', address2='DROP CODE 1094', city='INDIANAPOLIS', state='IN', country=None, postal_code='46285'), branding=Branding(icon_url='https://api.massive.com/v1/reference/company-branding/bGlsbHkuY29t/images/2025-04-04_icon.png', logo_url='https://api.massive.com/v1/reference/company-branding/bGlsbHkuY29t/images/2025-04-04_logo.svg', accent_color=None, light_color=None, dark_color=None), cik='0000059478', composite_figi='BBG000BNBDC2', currency_name='usd', currency_symbol=None, base_currency_name=None, base_currency_symbol=None, delisted_utc=None, description="Eli Lilly is a drug firm with a focus on neuroscience, cardiometabolic, cancer, and immunology. Lilly's key products include Verzenio for cancer; Mounjaro, Zepbound, Jardiance, Trulicity, Humalog, and Humulin for cardiometabolic; and Taltz and Olumiant for immunology.", ticker_root='LLY', ticker_suffix=None, homepage_url='https://www.lilly.com', list_date='1970-07-09', locale='us', market='stocks', market_cap=917644831176.96, name='Eli Lilly & Co.', phone_number='(317) 276-2000', primary_exchange='XNYS', share_class_figi='BBG001S5STL8', share_class_shares_outstanding=946456759, sic_code='2834', sic_description='PHARMACEUTICAL PREPARATIONS', ticker='LLY', total_employees=47000, type='CS', weighted_shares_outstanding=895018757)
```

## `get_ticker_events`

Sample output:

```python
TickerChangeResults(name='Eli Lilly & Co.', composite_figi='BBG000BNBDC2', cik='0000059478', events=[{'ticker_change': {'ticker': 'LLY'}, 'type': 'ticker_change', 'date': '2003-09-10'}])
```

## `get_ticker_types`

Sample output:

```python
[TickerTypes(asset_class='stocks', code='CS', description='Common Stock', locale='us'), TickerTypes(asset_class='stocks', code='PFD', description='Preferred Stock', locale='us'), TickerTypes(asset_class='stocks', code='WARRANT', description='Warrant', locale='us'), TickerTypes(asset_class='stocks', code='RIGHT', description='Rights', locale='us'), TickerTypes(asset_class='stocks', code='BOND', description='Corporate Bond', locale='us'), TickerTypes(asset_class='stocks', code='ETF', description='Exchange Traded Fund', locale='us'), TickerTypes(asset_class='stocks', code='ETN', description='Exchange Traded Note', locale='us'), TickerTypes(asset_class='stocks', code='ETV', description='Exchange Traded Vehicle', locale='us'), TickerTypes(asset_class='stocks', code='SP', description='Structured Product', locale='us'), TickerTypes(asset_class='stocks', code='ADRC', description='American Depository Receipt Common', locale='us'), TickerTypes(asset_class='stocks', code='ADRP', description='American Depository Receipt Preferred', locale='us'), TickerTypes(asset_class='stocks', code='ADRW', description='American Depository Receipt Warrants', locale='us'), TickerTypes(asset_class='stocks', code='ADRR', description='American Depository Receipt Rights', locale='us'), TickerTypes(asset_class='stocks', code='FUND', description='Fund', locale='us'), TickerTypes(asset_class='stocks', code='BASKET', description='Basket', locale='us'), TickerTypes(asset_class='stocks', code='UNIT', description='Unit', locale='us'), TickerTypes(asset_class='stocks', code='LT', description='Liquidating Trust', locale='us'), TickerTypes(asset_class='stocks', code='OS', description='Ordinary Shares', locale='us'), 
TickerTypes(asset_class='stocks', code='GDR', description='Global Depository Receipts', locale='us'), TickerTypes(asset_class='stocks', code='OTHER', description='Other Security Type', locale='us'), TickerTypes(asset_class='stocks', code='NYRS', description='New York Registry Shares', locale='us'), TickerTypes(asset_class='stocks', code='AGEN', description='Agency Bond', locale='us'), TickerTypes(asset_class='stocks', code='EQLK', description='Equity Linked Bond', locale='us'), TickerTypes(asset_class='stocks', code='ETS', description='Single-security ETF', locale='us'), TickerTypes(asset_class='indices', code='IX', description='Index', locale='us')]

```

## `list_aggs`

Sample output:

```python
Agg(open=1010.085, high=1032.95, low=1010.085, close=1022.87, volume=4153595.0, vwap=1025.3506, timestamp=1763010000000, transactions=180356, otc=None)
```

## `list_conditions`

Sample output:

```python
Condition(abbreviation=None, asset_class='crypto', data_types=['trade'], description=None, exchange=None, id=0, legacy=None, name='Regular Trade', sip_mapping=None, type='regular', update_rules=None)
```

## `list_dividends`

Sample output:

```python
Dividend(id='Ed4e7a23e8f984eb166b3506d814e00aa86243112a217d7ca0f2ec30546aa7da4', cash_amount=2.21, currency='USD', declaration_date='2025-11-07', dividend_type='CD', ex_dividend_date='2025-12-08', frequency=4, pay_date='2025-12-16', record_date='2025-12-08', ticker='UNH')
```

## `list_inflation`

Sample output:

```python
FedInflation(cpi=319.086, cpi_core=324.739, cpi_year_over_year=3.000483, date='2025-01-01', pce=125.417, pce_core=124.587, pce_spending=20462.2)
```

## `list_options_contracts`

Sample output:

```python
OptionsContract(additional_underlyings=None, cfi='OCASPS', contract_type='call', correction=None, exercise_style='american', expiration_date='2025-11-21', primary_exchange='BATO', shares_per_contract=100, strike_price=390, ticker='O:LLY251121C00390000', underlying_ticker='LLY')
```

## `list_short_interest`

Sample output:

```python
ShortInterest(avg_daily_volume=2380958, days_to_cover=5.12, settlement_date='2017-12-29', short_interest=12182388, ticker='LLY')
```

## `list_short_volume`

Sample output:

```python
ShortVolume(adf_short_volume=0, adf_short_volume_exempt=0, date='2024-02-06', exempt_volume=13740, nasdaq_carteret_short_volume=1773314, nasdaq_carteret_short_volume_exempt=12107, nasdaq_chicago_short_volume=21577, nasdaq_chicago_short_volume_exempt=0, non_exempt_volume=1862003, nyse_short_volume=80852, nyse_short_volume_exempt=1633, short_volume=1875743, short_volume_ratio=54.96, ticker='LLY', total_volume=3412616)
```

## `list_splits`

Sample output:

```python
Split(id='E0f5653c619604b99f1cb07e7a995b73f6ea613135f69c9356e436000fb66baa9', execution_date='2026-03-30', split_from=1, split_to=5, ticker='SGBKF')
```

## `list_ticker_news`

Sample output:

```python
TickerNews(amp_url=None, article_url='https://www.globenewswire.com/news-release/2025/11/14/3187993/0/es/Bitget-incluye-los-futuros-perpetuos-sobre-los-%C3%ADndices-burs%C3%A1tiles-LLY-MA-y-UNH-mientras-que-el-volumen-acumulado-de-operaciones-en-Bitget-alcanza-los-3-mil-millones.html', author='Bitget', description='Bitget expanded its real-world asset derivatives by introducing perpetual futures for stock indices of Eli Lilly, Montage Gold, and UnitedHealth Group, with up to 10x leverage and USDT settlement. The platform recently surpassed $3 billion in trading volume for stock index futures.', id='f67af2497084c847a6ac3f73e58f79e5a0126b4373f6c35cc6db75468d0002db', image_url='https://ml-eu.globenewswire.com/Resource/Download/1d6d5ad9-e478-4b92-a907-c63f166a3af9', insights=[Insight(sentiment='neutral', sentiment_reasoning='Company mentioned as part of new derivative product offering without specific positive or negative context', ticker='LLY'), Insight(sentiment='neutral', sentiment_reasoning='Company mentioned as part of new derivative product offering without specific positive or negative context', ticker='UNH')], keywords=['perpetual futures', 'stock indices', 'derivatives', 'tokenization', 'cryptocurrency'], published_utc='2025-11-14T05:54:00Z', publisher=Publisher(favicon_url='https://s3.massive.com/public/assets/news/favicons/globenewswire.ico', homepage_url='https://www.globenewswire.com', logo_url='https://s3.massive.com/public/assets/news/logos/globenewswire.svg', name='GlobeNewswire Inc.'), tickers=['LLY', 'UNH'], title='Bitget incluye los futuros perpetuos sobre los índices bursátiles LLY, MA y UNH, mientras que el volumen acumulado de operaciones en Bitget alcanza 
los $3 mil millones')
```

## `list_tickers`

Sample output:

```python
Ticker(active=True, cik='0000059478', composite_figi='BBG000BNBDC2', currency_name='usd', currency_symbol=None, base_currency_symbol=None, base_currency_name=None, delisted_utc=None, last_updated_utc='2025-11-15T07:06:07.224118319Z', locale='us', market='stocks', name='Eli Lilly & Co.', primary_exchange='XNYS', share_class_figi='BBG001S5STL8', ticker='LLY', type='CS', source_feed=None)
```

## `list_treasury_yields`

Sample output:

```python
TreasuryYield(date='1962-01-02', yield_1_month=None, yield_3_month=None, yield_6_month=None, yield_1_year=3.22, yield_2_year=None, 
yield_3_year=None, yield_5_year=3.88, yield_7_year=None, yield_10_year=4.06, yield_20_year=None, yield_30_year=None)
```
