# FRED

Here are the functions available under the free-tier API for FRED. Each section lists the function name and a sample output (truncated for brevity).

More info: https://fred.stlouisfed.org/docs/api/api_key.html

For initialization, check: https://pypi.org/project/fredapi/

---
## `get_series("AAPL")`

Sample output (pandas):

```json
2015-12-14    2021.94
2015-12-15    2043.41
2015-12-16    2073.07
2015-12-17    2041.89
2015-12-18    2005.55
               ...
2025-12-08    6846.51
2025-12-09    6840.51
2025-12-10    6886.68
2025-12-11    6901.00
2025-12-12    6827.41
Length: 2610, dtype: float64

```

## `get_series_all_releases("GDP")`

Sample output (pandas dataframe):

```json
           realtime_start                 date      value
0     1992-12-22 00:00:00  1946-01-01 00:00:00      199.7
1     1996-01-19 00:00:00  1946-01-01 00:00:00        NaT
2     1997-05-07 00:00:00  1946-01-01 00:00:00      210.4
3     1999-10-28 00:00:00  1946-01-01 00:00:00        NaT
4     1992-12-22 00:00:00  1946-04-01 00:00:00      207.7
...                   ...                  ...        ...
3226  2025-06-26 00:00:00  2025-01-01 00:00:00  29962.047
3227  2025-09-25 00:00:00  2025-01-01 00:00:00  30042.113
3228  2025-07-30 00:00:00  2025-04-01 00:00:00  30331.117
3229  2025-08-28 00:00:00  2025-04-01 00:00:00  30353.902
3230  2025-09-25 00:00:00  2025-04-01 00:00:00  30485.729

[3231 rows x 3 columns]
```

## `get_series_as_of_date("GDP")`

Sample output (pnadas dataframe):

```json
           realtime_start                 date      value
0     1992-12-22 00:00:00  1946-01-01 00:00:00      199.7
1     1996-01-19 00:00:00  1946-01-01 00:00:00        NaT
2     1997-05-07 00:00:00  1946-01-01 00:00:00      210.4
3     1999-10-28 00:00:00  1946-01-01 00:00:00        NaT
4     1992-12-22 00:00:00  1946-04-01 00:00:00      207.7
...                   ...                  ...        ...
3226  2025-06-26 00:00:00  2025-01-01 00:00:00  29962.047
3227  2025-09-25 00:00:00  2025-01-01 00:00:00  30042.113
3228  2025-07-30 00:00:00  2025-04-01 00:00:00  30331.117
3229  2025-08-28 00:00:00  2025-04-01 00:00:00  30353.902
3230  2025-09-25 00:00:00  2025-04-01 00:00:00  30485.729

[3231 rows x 3 columns]
```

## `get_series_first_release("GDP")`

Sample output (pandas dataframe):

```json
  return Index(sequences[0], name=names)
date
1946-01-01        199.7
1946-04-01        207.7
1946-07-01        217.9
1946-10-01        222.2
1947-01-01        226.7
                ...
2024-04-01    28629.153
2024-07-01    29349.924
2024-10-01     29700.58
2025-01-01    29977.632
2025-04-01    30331.117
Name: value, Length: 318, dtype: object
```

## `get_series_info("SP500")`

Sample output:

```python
id                                                                       SP500
realtime_start                                                      2025-12-12
realtime_end                                                        2025-12-12
title                                                                  S&P 500
observation_start                                                   2015-12-14
observation_end                                                     2025-12-12
frequency                                                         Daily, Close
frequency_short                                                              D
units                                                                    Index
units_short                                                              Index
seasonal_adjustment                                    Not Seasonally Adjusted
seasonal_adjustment_short                                                  NSA
last_updated                                            2025-12-12 19:02:25-06
popularity                                                                  91
notes                        The observations for the S&P 500 represent the...
dtype: object
```

## `get_series_latest_release("SP500")`

Sample output (pandas, dataframe):

```json
2015-12-14    2021.94
2015-12-15    2043.41
2015-12-16    2073.07
2015-12-17    2041.89
2015-12-18    2005.55
               ...
2025-12-08    6846.51
2025-12-09    6840.51
2025-12-10    6886.68
2025-12-11    6901.00
2025-12-12    6827.41
Length: 2610, dtype: float64
```

## `get_weekly`

Sample output (JSON; truncated):

```json
{
  "2025-12-05": {
    "1. open": "278.0100",
    "2. high": "288.6200",
    "3. low": "276.1400",
    "4. close": "278.7800",
    "5. volume": "235050842"
  },
  "2025-11-28": {
    "1. open": "270.9000",
    "2. high": "280.3800",
    "3. low": "270.9000",
    "4. close": "278.8500",
    "5. volume": "166067059"
  }
}

```

## `get_weekly_adjusted`

Sample output (JSON, truncated):

```json
{
  "2018-11-02": {
    "1. open": "219.1900",
    "2. high": "222.3600",
    "3. low": "205.4300",
    "4. close": "207.4800",
    "5. adjusted close": "49.1498",
    "6. volume": "270606277",
    "7. dividend amount": "0.0000"
  },
  "2018-10-26": {
    "1. open": "219.7900",
    "2. high": "224.2300",
    "3. low": "212.6700",
    "4. close": "216.3000",
    "5. adjusted close": "51.2391",
    "6. volume": "185599234",
    "7. dividend amount": "0.0000"
  }
}
```
## TechIndicators

## `get_ad`

Sample output (JSON; truncated):

```json
{
  "2014-02-13": { "Chaikin A/D": "66536858971.6203" },
  "2014-02-12": { "Chaikin A/D": "66253706164.8908" },
  "2014-02-11": { "Chaikin A/D": "66300506333.1946" },
}
```

## `get_adosc`

Sample output (JSON, truncated):

```json
{
  "2017-02-06": { "ADOSC": "170435881.5870" },
  "2017-02-03": { "ADOSC": "157576059.8067" },
  "2017-02-02": { "ADOSC": "152720518.8979" },
}

```

## `get_adx`

Sample output (JSON; truncated):

```json
{
  "2025-12-05": { "ADX": "23.8979" },
  "2025-11-28": { "ADX": "23.6851" },
  "2025-10-31": { "ADX": "23.6136" },
}

```

## `get_adxr`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": { "ADXR": "27.1498" },
  "2025-11-28": { "ADXR": "27.3426" },
  "2025-10-31": { "ADXR": "27.8617" },
}
```

## `get_apo`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": { "APO": "16.8315" },
  "2025-11-28": { "APO": "18.5993" },
  "2025-10-31": { "APO": "19.2612" },
}
```

## `get_aroon`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {"APO": "16.8315"},
  "2025-11-28": {"APO": "18.5993"},
  "2025-10-31": {"APO": "19.2612"},
}
```

## `get_aroonosc`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"AROONOSC": "100.0000"},
    "2025-11-28": {"AROONOSC": "95.0000"},
    "2025-10-31": {"AROONOSC": "90.0000"},
}
```

## `get_atr`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"ATR": "22.2268"},
    "2025-11-28": {"ATR": "22.7398"},
    "2025-10-31": {"ATR": "23.1440"},
}
```

## `get_bbands`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {
        "Real Upper Band": "280.3289",
        "Real Middle Band": "231.2995",
        "Real Lower Band": "182.2701"
    },
    "2025-11-28": {
        "Real Upper Band": "276.8925",
        "Real Middle Band": "225.8087",
        "Real Lower Band": "174.7249"
    }
}
```

## `get_cci`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"CCI": "184.6460"},
    "2025-11-28": {"CCI": "186.7051"},
    "2025-10-31": {"CCI": "161.1050"},
}
```

## `get_cmo`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"CMO": "36.4565"},
    "2025-11-28": {"CMO": "36.5019"},
    "2025-10-31": {"CMO": "33.8920"},
}

```

## `get_dema`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"DEMA": "258.3845"},
    "2025-11-28": {"DEMA": "251.1595"},
    "2025-10-31": {"DEMA": "242.6247"},
}
```

## `get_dx`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"DX": "27.9412"},
    "2025-11-28": {"DX": "25.0433"},
    "2025-10-31": {"DX": "23.8688"},
}
```

## `get_ema`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"EMA": "230.5377"},
    "2025-11-28": {"EMA": "225.4596"},
    "2025-10-31": {"EMA": "219.8395"},
}
```

## `get_ht_dcperiod`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"DCPERIOD": "20.4511"},
    "2025-11-28": {"DCPERIOD": "20.4545"},
    "2025-10-31": {"DCPERIOD": "20.1195"},
}

```

## `get_ht_dcphase`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"HT_DCPHASE": "221.8346"},
    "2025-11-28": {"HT_DCPHASE": "261.4913"},
    "2025-10-31": {"HT_DCPHASE": "255.4538"},
}

```

## `get_ht_phasor`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {
        "PHASE": "-7.5324",
        "QUADRATURE": "66.3869"
    },
    "2025-11-28": {
        "PHASE": "-23.4251",
        "QUADRATURE": "38.3305"
    },
}
```

## `get_ht_sine`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {
        "SINE": "-0.6670",
        "LEAD SINE": "-0.9985"
    },
    "2025-11-28": {
        "SINE": "-0.9890",
        "LEAD SINE": "-0.8039"
    },
}
```

## `get_ht_trendline`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"HT_TRENDLINE": "225.9198"},
    "2025-11-28": {"HT_TRENDLINE": "220.8257"},
    "2025-10-31": {"HT_TRENDLINE": "216.3659"},
}
```

## `get_ht_trendmode`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"TRENDMODE": "1"},
    "2025-11-28": {"TRENDMODE": "1"},
    "2025-10-31": {"TRENDMODE": "1"},
}
```

## `get_kama`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"KAMA": "226.4473"},
    "2025-11-28": {"KAMA": "219.2775"},
    "2025-10-31": {"KAMA": "211.3293"},
}
```

## `get_macdext`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {
        "MACD": "16.8315",
        "MACD_Signal": "20.5834",
        "MACD_Hist": "-3.7519"
    },
    "2025-11-28": {
        "MACD": "18.5993",
        "MACD_Signal": "21.3962",
        "MACD_Hist": "-2.7969"
    },
}
```

## `get_mama`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {
        "MAMA": "101.4353",
        "FAMA": "21.1844"
    },
    "2025-11-28": {
        "MAMA": "99.6439",
        "FAMA": "20.7811"
    },
}
```

## `get_mfi`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"MFI": "73.3965"},
    "2025-11-28": {"MFI": "70.0331"},
    "2025-10-31": {"MFI": "65.2527"},
}

```

## `get_midpoint`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"MIDPOINT": "234.9092"},
    "2025-11-28": {"MIDPOINT": "223.9069"},
    "2025-10-31": {"MIDPOINT": "219.5366"},
}
```

## `get_midprice`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"MIDPRICE": "228.1868"},
    "2025-11-28": {"MIDPRICE": "221.5695"},
    "2025-10-31": {"MIDPRICE": "219.9058"},
}
```

## `get_minus_di`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"MINUS_DI": "17.2743"},
    "2025-11-28": {"MINUS_DI": "17.7733"},
    "2025-10-31": {"MINUS_DI": "18.3820"},
}
```

## `get_minus_dm`

Sample output (JSON, truncated):

```json
{
    "2025-12-05": {"MINUS_DM": "76.7907"},
    "2025-11-28": {"MINUS_DM": "80.8324"},
    "2025-10-31": {"MINUS_DM": "85.0867"},
}
```

## `get_mom`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "MOM": "109.8162"
  },
  "2025-11-28": {
    "MOM": "108.7454"
  },
  "2025-10-31": {
    "MOM": "90.8091"
  },
}
```

## `get_natr`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "NATR": "7.9729"
  },
  "2025-11-28": {
    "NATR": "8.1549"
  },
  "2025-10-31": {
    "NATR": "8.5684"
  },
}
```

## `get_obv`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "OBV": "416772828856.0000"
  },
  "2025-11-28": {
    "OBV": "417007879698.0000"
  },
  "2025-10-31": {
    "OBV": "416131398245.0000"
  },
}
```

## `get_plus_di`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "PLUS_DI": "30.6708"
  },
  "2025-11-28": {
    "PLUS_DI": "29.6496"
  },
  "2025-10-31": {
    "PLUS_DI": "29.9083"
  },
}

```

## `get_plus_dm`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "PLUS_DM": "136.3428"
  },
  "2025-11-28": {
    "PLUS_DM": "134.8450"
  },
  "2025-10-31": {
    "PLUS_DM": "138.4397"
  },
}
```

## `get_ppo`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "PPO": "7.6695"
  },
  "2025-11-28": {
    "PPO": "8.6413"
  },
  "2025-10-31": {
    "PPO": "9.1273"
  },
}
```

## `get_roc`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "ROC": "64.9939"
  },
  "2025-11-28": {
    "ROC": "63.9285"
  },
  "2025-10-31": {
    "ROC": "50.6464"
  },
}
```

## `get_rocr`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "ROCR": "1.6499"
  },
  "2025-11-28": {
    "ROCR": "1.6393"
  },
  "2025-10-31": {
    "ROCR": "1.5065"
  },
}
```

## `get_rsi`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "RSI": "68.2282"
  },
  "2025-11-28": {
    "RSI": "68.2510"
  },
  "2025-10-31": {
    "RSI": "66.9460"
  },}
```

## `get_sar`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "SAR": "174.9441"
  },
  "2025-11-28": {
    "SAR": "171.6832"
  },
  "2025-10-31": {
    "SAR": "169.5328"
  },
}
```

## `get_sma`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "SMA": "231.2995"
  },
  "2025-11-28": {
    "SMA": "225.8087"
  },
  "2025-10-31": {
    "SMA": "220.3714"
  },
}
```

## `get_stoch`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "SlowK": "92.8012",
    "SlowD": "93.9957"
  },
  "2025-11-28": {
    "SlowK": "95.0203",
    "SlowD": "90.0105"
  },
}
```

## `get_stochf`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "FastK": "88.7600",
    "FastD": "92.8012"
  },
  "2025-11-28": {
    "FastK": "98.0707",
    "FastD": "95.0203"
  },
}
```

## `get_stochrsi`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {
    "FastK": "99.7113",
    "FastD": "99.9038"
  },
  "2025-11-28": {
    "FastK": "100.0000",
    "FastD": "100.0000"
  },
}
```

## `get_t3`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {"T3": "226.0747"},
  "2025-11-28": {"T3": "223.3575"},
  "2025-10-31": {"T3": "220.8686"},
}
```

## `get_tema`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {"TEMA": "263.7496"},
  "2025-11-28": {"TEMA": "254.9424"},
  "2025-10-31": {"TEMA": "243.8910"},
}
```

## `get_trange`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {"TRANGE": "12.4800"},
  "2025-11-28": {"TRANGE": "15.0600"},
  "2025-10-31": {"TRANGE": "33.2879"},
}
```

## `get_trima`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {"TRIMA": "228.0487"},
  "2025-11-28": {"TRIMA": "226.5477"},
  "2025-10-31": {"TRIMA": "224.8002"}
}
```

## `get_trix`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {"TRIX": "1.3307"},
  "2025-11-28": {"TRIX": "1.3143"},
  "2025-10-31": {"TRIX": "1.3073"},
}
```

## `get_ultosc`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {"ULTOSC": "72.0913"},
  "2025-11-28": {"ULTOSC": "71.6268"},
  "2025-10-31": {"ULTOSC": "71.4724"}
}
```

## `get_willr`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {"WILLR": "-8.1412"},
  "2025-11-28": {"WILLR": "-1.3008"},
  "2025-10-31": {"WILLR": "-6.0750"},
}
```
## `get_wma`

Sample output (JSON, truncated):

```json
{
  "2025-12-05": {"WMA": "238.9934"},
  "2025-11-28": {"WMA": "233.9485"},
  "2025-10-31": {"WMA": "228.3791"},
}
```
## AlphaIntelligence
## `get_most_active`

Sample output:

```python
(   ticker   price change_amount change_percentage      volume
0    PAVS  0.0366        0.0051          16.1905%  1035724634
1    SOXS    3.02          -0.1          -3.2051%   297378402
2     WBD   26.08          1.54           6.2755%   197434646
3    IRBT    3.69          0.66          21.7822%   144697722
4    NVDA  182.41         -0.97           -0.529%   142049339
5    SOFI   27.78         -1.82          -6.1486%   135047309
6    INHD   0.154        0.0152           10.951%   134970079
7     EWZ   32.55         -2.17            -6.25%   134455617
8    NFLX  100.24         -2.98           -2.887%   132353385
9    BBAI    6.82          -0.2           -2.849%   113179053
10   ASST  0.9005       -0.0761          -7.7923%   108205661
11   TDIC  0.3937        0.1129          40.2066%   105426342
12   BYND    1.22         -0.02          -1.6129%    99338409
13   INTC   41.41          0.91           2.2469%    98969513
14    TZA    7.21          0.09            1.264%    94144267
15   PLUG     2.2         -0.03          -1.3453%    93910445
16   WHLR    6.41          3.17          97.8395%    86502522
17   ONDS    9.07         -0.12          -1.3058%    81931946
18    SPY  685.66          1.27           0.1856%    77073647
19   VALE    12.9         -0.66          -4.8673%    76750672, None)
```

## `get_news_sentiment`

Sample output (truncated):

```python
(                                                title                                                url  ... overall_sentiment_label                                   ticker_sentiment0    Apple Chip Chief Johny Srouji 'Seriously Cons...  https://www.benzinga.com/markets/tech/25/12/49...  ...                 Neutral  [{'ticker': 'AAPL', 'relevance_score': '0.9754... 
1     SPDR S&P 500 ETF Trust Sees Positive Fund Flows  https://www.tipranks.com/news/weekend-updates/...  ...                 Bullish  [{'ticker': 'SPY', 'relevance_score': '0.97406... 
2   iOS 26.2 Will Add Two New Features To CarPlay ...  https://www.bgr.com/2042875/ios-26-2-new-carpl...  ...                 Bullish  [{'ticker': 'AAPL', 'relevance_score': '0.9718... 
3   Intel Stock (INTC) on December 6, 2025: Nvidia...  https://ts2.tech/en/intel-stock-intc-on-decemb...  ...        Somewhat-Bullish  [{'ticker': 'INTC', 'relevance_score': '0.9717... 
4    Amundi Has $423.53 Million Stock Holdings in ...  https://www.marketbeat.com/instant-alerts/fili...  ...                 Neutral  [{'ticker': 'SYK', 'relevance_score': '0.97956... 
)
```

## `get_top_gainers`

Sample output:

```python
(   ticker   price change_amount change_percentage     volume
0     TGL   25.44        18.682         276.4427%   20707306
1     SMX  331.98        190.98         135.4468%    3813519
2    WHLR    6.41          3.17          97.8395%   86502522
3   NIXXW   0.052        0.0231          79.9308%      10351
4   CCGWW    0.04        0.0144            56.25%       6690
5   OUSTZ    0.08        0.0285          55.3398%      34539
6   SMXWW   0.285          0.09          46.1538%    4070131
7    DBRG  14.145         4.425          45.5247%   55784726
8   FOXXW  0.1603        0.0498          45.0679%      95118
9   PLMKW  0.4908        0.1508          44.3529%         20
10   TDIC  0.3937        0.1129          40.2066%  105426342
11   TORO     5.8          1.66          40.0966%   15359487
12  ATMCW    0.07        0.0199          39.7206%      17497
13   LICN    4.07          1.13          38.4354%     700529
14  GIPRW    0.07        0.0194          38.3399%       3010
15   SPHL    4.53           1.2           36.036%     419680
16   ALMS   11.12          2.82          33.9759%    4341824
17   PW-A     5.0          1.25          33.3333%       4946
18  AREBW   0.024         0.006          33.3333%      43972
19  BZFDW  0.0359        0.0089           32.963%       1710, None)
```

## `get_top_losers`

Sample output:

```python
(   ticker   price change_amount change_percentage    volume
0   HSCSW   0.035       -0.0444         -55.9194%     51619
1   BTBDW  0.1293       -0.0994         -43.4631%      2191
2   ACONW   0.045         -0.03            -40.0%    102454
3    AHMA    8.22         -4.98         -37.7273%   1050207
4    QNRX   12.09         -6.82         -36.0656%    536539
5    JFBR     1.6          -0.9            -36.0%  38355192
6   SAIHW  0.0793       -0.0407         -33.9167%    113117
7   ESLAW    0.07       -0.0357         -33.7748%       360
8   WALDW  0.0398       -0.0197         -33.1092%      7520
9    SPWH    1.72         -0.73         -29.7959%   7295812
10  MYPSW  0.0101       -0.0042         -29.3706%     16749
11  CELUW  0.0178       -0.0069         -27.9352%       750
12   XCUR    4.88        -1.785         -26.7817%    167085
13  HUBCZ  0.0068       -0.0024          -26.087%    200440
14  BRRWW  0.6119       -0.2081          -25.378%    264111
15  CGCTW     0.3          -0.1            -25.0%     16960
16   DOMO   8.835        -2.735         -23.6387%   4599035
17  PRENW   0.022       -0.0064         -22.5352%       372
18   CODI   5.725        -1.655         -22.4255%   4094275
19  NMPAR  0.2051        -0.059           -22.34%      5125, None)
```
# EconIndicators
## `get_cpi`

Sample output:

```python
(            date    value
0     2025-09-01  324.800
1     2025-08-01  323.976
2     2025-07-01  323.048
3     2025-06-01  322.561
4     2025-05-01  321.465
...          ...      ...
1348  1913-05-01    9.700
1349  1913-04-01    9.800
1350  1913-03-01    9.800
1351  1913-02-01    9.800
1352  1913-01-01    9.800

[1353 rows x 2 columns], None)
```

## `get_durables`

Sample output:

```python
(           date     value
0    2025-09-01  334731.0
1    2025-08-01  311536.0
2    2025-07-01  284519.0
3    2025-06-01  330862.0
4    2025-05-01  343734.0
..          ...       ...
399  1992-06-01    131268
400  1992-05-01    122274
401  1992-04-01    123268
402  1992-03-01    129309
403  1992-02-01    118429

[404 rows x 2 columns], None)
```

## `get_ffr`

Sample output:

```python
(           date value
0    2025-11-01  3.88
1    2025-10-01  4.09
2    2025-09-01  4.22
3    2025-08-01  4.33
4    2025-07-01  4.33
..          ...   ...
852  1954-11-01  0.83
853  1954-10-01  0.85
854  1954-09-01  1.07
855  1954-08-01  1.22
856  1954-07-01  0.80

[857 rows x 2 columns], None)
```

## `get_inflation`

Sample output:

```python
(          date             value
0   2024-01-01  2.94952520485207
1   2023-01-01  4.11633838374488
2   2022-01-01  8.00279982052121
3   2021-01-01  4.69785886363742
4   2020-01-01  1.23358439630629
..         ...               ...
60  1964-01-01  1.27891156462591
61  1963-01-01  1.23966942148753
62  1962-01-01  1.19877334820186
63  1961-01-01  1.07072414764724
64  1960-01-01  1.45797598627791

[65 rows x 2 columns], None)
```

## `get_nonfarm`

Sample output:

```python
(            date   value
0     2025-09-01  159732
1     2025-08-01  159415
2     2025-07-01  159219
3     2025-06-01  160256
4     2025-05-01  159930
...          ...     ...
1036  1939-05-01   30145
1037  1939-04-01   29786
1038  1939-03-01   29804
1039  1939-02-01   29394
1040  1939-01-01   29296

[1041 rows x 2 columns], None)
```

## `get_real_gdp`

Sample output:

```python
(          date      value
0   2024-01-01  23358.435
1   2023-01-01  22723.719
2   2022-01-01  22075.931
3   2021-01-01  21532.407
4   2020-01-01    20284.5
..         ...        ...
91  1933-01-01    877.431
92  1932-01-01    888.414
93  1931-01-01   1019.977
94  1930-01-01   1089.785
95  1929-01-01   1191.124

[96 rows x 2 columns], None)
```

## `get_real_gdp_per_capita`

Sample output:

```python
(           date    value
0    2025-04-01  69499.0
1    2025-01-01  68937.0
2    2024-10-01  69136.0
3    2024-07-01  68926.0
4    2024-04-01  68504.0
..          ...      ...
309  1948-01-01  15371.0
310  1947-10-01  15204.0
311  1947-07-01  15039.0
312  1947-04-01  15139.0
313  1947-01-01  15248.0

[314 rows x 2 columns], None)
```

## `get_retail_sales`

Sample output:

```python
(           date     value
0    2025-09-01  610952.0
1    2025-08-01  640896.0
2    2025-07-01  644493.0
3    2025-06-01  616031.0
4    2025-05-01  647306.0
..          ...       ...
400  1992-05-01  147550.0
401  1992-04-01  142314.0
402  1992-03-01  137978.0
403  1992-02-01  127022.0
404  1992-01-01  126717.0

[405 rows x 2 columns], None)
```

## `get_treasury_yield`

Sample output:

```python
(           date value
0    2025-11-01  4.09
1    2025-10-01  4.06
2    2025-09-01  4.12
3    2025-08-01  4.26
4    2025-07-01  4.39
..          ...   ...
867  1953-08-01  2.95
868  1953-07-01  2.93
869  1953-06-01  3.11
870  1953-05-01  3.05
871  1953-04-01  2.83

[872 rows x 2 columns], None)
```

## `get_unemployment`

Sample output:

```python
(           date value
0    2025-09-01   4.4
1    2025-08-01   4.3
2    2025-07-01   4.2
3    2025-06-01   4.1
4    2025-05-01   4.2
..          ...   ...
928  1948-05-01   3.5
929  1948-04-01   3.9
930  1948-03-01   4.0
931  1948-02-01   3.8
932  1948-01-01   3.4

[933 rows x 2 columns], None)
```

# FundamentalData
## `get_balance_sheet_annual`

Sample output:

```python
(   fiscalDateEnding reportedCurrency   totalAssets totalCurrentAssets  ... treasuryStock retainedEarnings  commonStock commonStockSharesOutstanding
0        2025-09-30              USD  359241000000       147957000000  ...          None     -14264000000  93568000000                  15004697000
1        2024-09-30              USD  364980000000       152987000000  ...          None     -19154000000  83276000000                  15408095000
2        2023-09-30              USD  352583000000       143566000000  ...          None       -214000000  73812000000                  15812547000
3        2022-09-30              USD  352755000000       135405000000  ...          None      -3068000000  64849000000                  16325819000
4        2021-09-30              USD  351002000000       134836000000  ...          None       5562000000  57365000000                  16864919000
5        2020-09-30              USD  323888000000       143713000000  ...          None      14966000000  50779000000                  17528214000
6        2019-09-30              USD  338516000000       162819000000  ...          None      45898000000  45174000000                  18595652000
7        2018-09-30              USD  365725000000       131339000000  ...          None      70400000000  40201000000                  20000436000
8        2017-09-30              USD  375319000000       128645000000  ...             0      98330000000  35867000000                  21006768000
9        2016-09-30              USD  321686000000       106869000000  ...          None      96364000000  31251000000                  22001124000
10       2015-09-30              USD  290479000000        89378000000  ...             0      92284000000  27416000000                  23172276000
11       2014-09-30              USD  231839000000        68531000000  ...             0      87152000000  23313000000                  24490652000
12       2013-09-30              USD  207000000000        73286000000  ...             0     104256000000  19764000000                  26086536000
13       2012-09-30              USD  176064000000        57653000000  ...             0     101289000000  16422000000                  26469940000
14       2011-09-30              USD  116371000000        44988000000  ...             0      62841000000  13331000000                  26226060000
15       2010-09-30              USD   75183000000        41678000000  ...             0      37169000000  10668000000                  25891936000
16       2009-09-30              USD   53851000000        36265000000  ...             0      19538000000   8210000000                  25396140000
17       2008-09-30              USD   39572000000        34690000000  ...          None      13845000000   7177000000                  25259892000
18       2007-09-30              USD   25347000000        21956000000  ...          None       9101000000   5368000000                  24900176000
19       2006-09-30              USD   17205000000        14509000000  ...          None       5607000000   4355000000                  24570728000

[20 rows x 38 columns], 'AAPL')
```

## `get_balance_sheet_quarterly`

Sample output:

```python
(   fiscalDateEnding reportedCurrency   totalAssets totalCurrentAssets  ... treasuryStock retainedEarnings  commonStock commonStockSharesOutstanding
0        2025-09-30              USD  359241000000       147957000000  ...          None     -14264000000  93568000000                  15004697000
1        2025-06-30              USD  331495000000       122491000000  ...          None     -17607000000  89806000000                  14948179000
2        2025-03-31              USD  331233000000       118674000000  ...          None     -15552000000  88711000000                  15056133000
3        2024-12-31              USD  344085000000       133240000000  ...          None     -11221000000  84768000000                  15150865000
4        2024-09-30              USD  364980000000       152987000000  ...          None     -19154000000  83276000000                  15408095000
..              ...              ...           ...                ...  ...           ...              ...          ...                          ...
76       2006-09-30              USD   17205000000        13758000000  ...          None       5607000000   4355000000                  24538304000
77       2006-06-30              USD   15114000000        11486000000  ...          None       5065000000   4249000000                  24538304000
78       2006-03-31              USD   13911000000        10730000000  ...          None       4673000000   4014000000                  24599036000
79       2005-12-31              USD   14181000000        11691000000  ...          None       4570000000   3815000000                  24477796000
80       2005-09-30              USD   11551000000         9969000000  ...          None       4005000000   3521000000                  24477796000

[81 rows x 38 columns], 'AAPL')
```

## `get_cash_flow_annual`

Sample output:

```python
(   fiscalDateEnding reportedCurrency operatingCashflow paymentsForOperatingActivities  ... proceedsFromSaleOfTreasuryStock changeInCashAndCashEquivalents changeInExchangeRate     netIncome
0        2025-09-30              USD      111482000000                           None  ...                            None                           None                 None  112010000000
1        2024-09-30              USD      118254000000                           None  ...                            None                           None                 None   93736000000
2        2023-09-30              USD      110543000000                           None  ...                            None                     5760000000                 None   96995000000
3        2022-09-30              USD      122151000000                           None  ...                            None                   -10952000000                 None   99803000000
4        2021-09-30              USD      104038000000                           None  ...                            None                    -3860000000                 None   94680000000
5        2020-09-30              USD       80674000000                           None  ...                            None                   -10435000000                 None   57411000000
6        2019-09-30              USD       69391000000                           None  ...                            None                    24311000000                 None   55256000000
7        2018-09-30              USD       77434000000                           None  ...                            None                     5624000000                 None   59531000000
8        2017-09-30              USD       63598000000                           None  ...                            None                     -195000000                 None   48351000000
9        2016-09-30              USD       65824000000                           None  ...                            None                     -636000000                 None   45687000000
10       2015-09-30              USD       81266000000                           None  ...                            None                     7276000000                 None   53394000000
11       2014-09-30              USD       59713000000                           None  ...                            None                     -415000000                 None   39510000000
12       2013-09-30              USD       53666000000                           None  ...                            None                     3513000000                 None   37037000000
13       2012-09-30              USD       50856000000                           None  ...                            None                      931000000                 None   41733000000
14       2011-09-30              USD       37529000000                           None  ...                            None                    -1446000000                 None   25922000000
15       2010-09-30              USD       18595000000                           None  ...                            None                     5998000000                 None   14013000000
16       2009-09-30              USD       10159000000                           None  ...                            None                    -6612000000                 None    5704000000
17       2008-09-30              USD        9596000000                           None  ...                            None                     2523000000                 None    4834000000
18       2007-09-30              USD        5470000000                           None  ...                            None                     2960000000                 None    3496000000
19       2006-09-30              USD        2220000000                           None  ...                            None                     2901000000                 None    1989000000

[20 rows x 29 columns], 'AAPL')
```

## `get_cash_flow_quarterly`

Sample output:

```python
(   fiscalDateEnding reportedCurrency operatingCashflow paymentsForOperatingActivities  ... proceedsFromSaleOfTreasuryStock changeInCashAndCashEquivalents changeInExchangeRate    netIncome
0        2025-09-30              USD       29728000000                           None  ...                            None                           None                 None  27466000000
1        2025-06-30              USD       27867000000                           None  ...                            None                           None                 None  23434000000
2        2025-03-31              USD       23952000000                           None  ...                            None                           None                 None  24780000000
3        2024-12-31              USD       29935000000                           None  ...                            None                           None                 None  36330000000
4        2024-09-30              USD       26811000000                           None  ...                            None                           None                 None  14736000000
..              ...              ...               ...                            ...  ...                             ...                            ...                  ...          ...
76       2006-09-30              USD        1055000000                           None  ...                            None                    -1621000000                 None    542000000
77       2006-06-30              USD        1007000000                           None  ...                            None                     1667000000                 None    472000000
78       2006-03-31              USD        -125000000                           None  ...                            None                     2196000000                 None    410000000
79       2005-12-31              USD         283000000                           None  ...                            None                      659000000                 None    565000000
80       2005-09-30              USD         752000000                           None  ...                            None                      397000000                 None    430000000

[81 rows x 29 columns], 'AAPL')
```

## `get_company_overview`

Sample output:

```json
{
  "Symbol": "AAPL",
  "AssetType": "Common Stock",
  "Name": "Apple Inc",
  "Description": "Apple Inc. is a leading American multinational technology company that specializes in innovative consumer electronics, software, and online services. With a record revenue of $274.5 billion in 2020, it holds the title of the world's most valuable publicly traded company and is a dominant force in the global technology landscape. Its flagship products, such as the iPhone, iPad, and Mac, have cemented its reputation as a trailblazer in the sector, positioning it as the fourth-largest PC vendor and smartphone manufacturer worldwide. As a cornerstone of the 'Big Five' technology companies, Apple continues to set industry standards and drive advancements in technology and consumer engagement.",
  "CIK": "320193",
  "Exchange": "NASDAQ",
  "Currency": "USD",
  "Country": "USA",
  "Sector": "TECHNOLOGY",
  "Industry": "CONSUMER ELECTRONICS",
  "Address": "ONE APPLE PARK WAY, CUPERTINO, CA, UNITED STATES, 95014",
  "OfficialSite": "https://www.apple.com",
  "FiscalYearEnd": "September",
  "LatestQuarter": "2025-09-30",
  "MarketCapitalization": "4137203794000",
  "EBITDA": "144748003000",
  "PERatio": "37.32",
  "PEGRatio": "2.876",
  "BookValue": "4.991",
  "DividendPerShare": "1.02",
  "DividendYield": "0.0036",
  "EPS": "7.47",
  "RevenuePerShareTTM": "27.84",
  "ProfitMargin": "0.269",
  "OperatingMarginTTM": "0.317",
  "ReturnOnAssetsTTM": "0.23",
  "ReturnOnEquityTTM": "1.714",
  "RevenueTTM": "416161006000",
  "GrossProfitTTM": "195201008000",
  "DilutedEPSTTM": "7.47",
  "QuarterlyEarningsGrowthYOY": "0.912",
  "QuarterlyRevenueGrowthYOY": "0.079",
  "AnalystTargetPrice": "283.58",
  "AnalystRatingStrongBuy": "5",
  "AnalystRatingBuy": "24",
  "AnalystRatingHold": "15",
  "AnalystRatingSell": "1",
  "AnalystRatingStrongSell": "3",
  "TrailingPE": "37.32",
  "ForwardPE": "34.25",
  "PriceToSalesRatioTTM": "9.94",
  "PriceToBookRatio": "56.94",
  "EVToRevenue": "10.19",
  "EVToEBITDA": "29.31",
  "Beta": "1.107",
  "52WeekHigh": "288.62",
  "52WeekLow": "168.63",
  "50DayMovingAverage": "265.59",
  "200DayMovingAverage": "228.15",
  "SharesOutstanding": "14776353000",
  "SharesFloat": "14750642000",
  "PercentInsiders": "1.697",
  "PercentInstitutions": "64.400",
  "DividendDate": "2025-11-13",
  "ExDividendDate": "2025-11-10"
}

```

## `get_dividends`

Sample output:

```python
(   ex_dividend_date declaration_date record_date payment_date amount
0        2025-11-10       2025-10-30  2025-11-10   2025-11-13   0.26
1        2025-08-11       2025-07-31  2025-08-11   2025-08-14   0.26
2        2025-05-12       2025-05-01  2025-05-12   2025-05-15   0.26
3        2025-02-10       2025-01-30  2025-02-10   2025-02-13   0.25
4        2024-11-08       2024-10-31  2024-11-11   2024-11-14   0.25
5        2024-08-12       2024-08-01  2024-08-12   2024-08-15   0.25
6        2024-05-10       2024-05-02  2024-05-13   2024-05-16   0.25
7        2024-02-09       2024-02-01  2024-02-12   2024-02-15   0.24
8        2023-11-10       2023-11-02  2023-11-13   2023-11-16   0.24
9        2023-08-11             None        None         None   0.24
10       2023-05-12       2023-05-04  2023-05-15   2023-05-18   0.24
11       2023-02-10       2023-02-02  2023-02-13   2023-02-16   0.23
12       2022-12-23       2022-12-19  2022-12-28   2023-01-09    0.0
13       2022-11-04       2022-10-27  2022-11-07   2022-11-10   0.23
14       2022-08-05       2022-07-28  2022-08-08   2022-08-11   0.23
15       2022-05-06       2022-04-28  2022-05-09   2022-05-12   0.23
16       2022-02-04       2022-01-27  2022-02-07   2022-02-10   0.22
17       2021-11-05       2021-10-28  2021-11-08   2021-11-11   0.22
18       2021-08-06             None        None         None   0.22
19       2021-05-07       2021-04-28  2021-05-10   2021-05-13   0.22
20       2021-02-05       2021-01-27  2021-02-08   2021-02-11  0.205
21       2020-11-06             None        None         None  0.205
22       2020-08-07       2020-07-30  2020-08-10   2020-08-13   0.82
23       2020-05-08             None        None         None   0.82
24       2020-02-07             None        None         None   0.77
25       2019-11-07             None        None         None   0.77
26       2019-08-09             None        None         None   0.77
27       2019-05-10             None        None         None   0.77
28       2019-02-08             None        None         None   0.73
29       2018-11-08             None        None         None   0.73
30       2018-08-10             None        None         None   0.73
31       2018-05-11             None        None         None   0.73
32       2018-02-09             None        None         None   0.63
33       2017-11-10             None        None         None   0.63
34       2017-08-10             None        None         None   0.63
35       2017-05-11             None        None         None   0.63
36       2017-02-09             None        None         None   0.57
37       2016-11-03             None        None         None   0.57
38       2016-08-04             None        None         None   0.57
39       2016-05-05             None        None         None   0.57
40       2016-02-04             None        None         None   0.52
41       2015-11-05             None        None         None   0.52
42       2015-08-06             None        None         None   0.52
43       2015-05-07             None        None         None   0.52
44       2015-02-05             None        None         None   0.47
45       2014-11-06             None        None         None   0.47
46       2014-08-07             None        None         None   0.47
47       2014-05-08             None        None         None   3.29
48       2014-02-06             None        None         None   3.05
49       2013-11-06             None        None         None   3.05
50       2013-08-08             None        None         None   3.05
51       2013-05-09             None        None         None   3.05
52       2013-02-07             None        None         None   2.65
53       2012-11-07             None        None         None   2.65
54       2012-08-09             None        None         None   2.65, 'AAPL')
```

## `get_earnings_annual`

Sample output:

```python
(   fiscalDateEnding reportedEPS
0        2025-09-30        7.47
1        2024-09-30        6.08
2        2023-09-30        6.12
3        2022-09-30        6.11
4        2021-09-30        5.62
5        2020-09-30        3.27
6        2019-09-30        2.98
7        2018-09-30        2.97
8        2017-09-30         2.3
9        2016-09-30      2.0675
10       2015-09-30         2.3
11       2014-09-30      1.6075
12       2013-09-30       1.415
13       2012-09-30      1.5775
14       2011-09-30      0.9875
15       2010-09-30        0.54
16       2009-09-30      0.2225
17       2008-09-30        0.19
18       2007-09-30        0.14
19       2006-09-30        0.08
20       2005-09-30        0.04
21       2004-09-30        0.05
22       2003-09-30      0.0112
23       2002-09-30      0.0198
24       2001-09-30      0.0064
25       2000-09-30        0.04
26       1999-09-30        0.05
27       1998-09-30        0.04
28       1997-09-30     -0.1114
29       1996-09-30     -0.1082, 'AAPL')
```

## `get_earnings_quarterly`

Sample output:

```python
(    fiscalDateEnding reportedDate reportedEPS estimatedEPS surprise surprisePercentage   reportTime
0         2025-09-30   2025-10-30        1.85         1.76     0.09             5.1136  post-market
1         2025-06-30   2025-07-31        1.57         1.43     0.14             9.7902  post-market
2         2025-03-31   2025-05-01        1.65         1.62     0.03             1.8519  post-market
3         2024-12-31   2025-01-30         2.4         2.34     0.06             2.5641  post-market
4         2024-09-30   2024-10-31        0.97         0.95     0.02             2.1053  post-market
..               ...          ...         ...          ...      ...                ...          ...
114       1997-03-31   1997-04-16       -0.05        -0.04    -0.01                -25   pre-market
115       1996-12-31   1997-01-15       -0.03        -0.02    -0.01                -50   pre-market
116       1996-09-30   1996-10-16      0.0018        -0.01   0.0118                118   pre-market
117       1996-06-30   1996-07-17       -0.02        -0.04     0.02                 50   pre-market
118       1996-03-31   1996-04-17       -0.07        -0.05    -0.02                -40   pre-market

[119 rows x 7 columns], 'AAPL')
```

## `get_income_statement_annual`

Sample output:

```python
(   fiscalDateEnding reportedCurrency   grossProfit  totalRevenue costOfRevenue  ... netIncomeFromContinuingOperations comprehensiveIncomeNetOfTax          ebit        ebitda     netIncome
0        2025-09-30              USD  195201000000  416161000000  220960000000  ...                      112010000000                        None  132729000000  144427000000  112010000000
1        2024-09-30              USD  180683000000  391035000000  210352000000  ...                       93736000000                        None  123216000000  134661000000   93736000000
2        2023-09-30              USD  169148000000  383285000000  214137000000  ...                       96995000000                        None  114301000000  125820000000   96995000000
3        2022-09-30              USD  170782000000  394328000000  223546000000  ...                       99803000000                        None  119437000000  130541000000   99803000000
4        2021-09-30              USD  152836000000  365817000000  212981000000  ...                       94680000000                        None  111852000000  123136000000   94680000000
5        2020-09-30              USD  104956000000  274515000000  169559000000  ...                       57411000000                        None   69964000000   81020000000   57411000000
6        2019-09-30              USD   98392000000  260174000000  161782000000  ...                       55256000000                        None   69313000000   81860000000   55256000000
7        2018-09-30              USD  101839000000  265595000000  163756000000  ...                       59531000000                        None   76143000000   87046000000   59531000000
8        2017-09-30              USD   88186000000  229234000000  141048000000  ...                       48351000000                        None   66412000000   76569000000   48351000000
9        2016-09-30              USD   84263000000  215639000000  131376000000  ...                       45687000000                        None   62828000000   73333000000   45687000000
10       2015-09-30              USD   93626000000  233715000000  140089000000  ...                       53394000000                        None   73248000000   84505000000   53394000000
11       2014-09-30              USD   70537000000  182795000000  112258000000  ...                       39510000000                        None   53867000000   61813000000   39510000000
12       2013-09-30              USD   64304000000  170910000000  106606000000  ...                       37037000000                        None   50291000000   57048000000   37037000000
13       2012-09-30              USD   68662000000  156508000000   87846000000  ...                       41733000000                        None   55763000000   59040000000   41733000000
14       2011-09-30              USD   43818000000  108249000000   64431000000  ...                       25922000000                        None   34205000000   36019000000   25922000000
15       2010-09-30              USD   25684000000   65225000000   39541000000  ...                       14013000000                        None   18385000000   19412000000   14013000000
16       2009-09-30              USD   17222000000   42905000000   25683000000  ...                        8235000000                        None   11740000000   12474000000    8235000000
17       2008-09-30              USD   11145000000   32479000000   21334000000  ...                              None                        None    6895000000    7304000000    4834000000
18       2007-09-30              USD    8154000000   24006000000   15852000000  ...                              None                        None    4407000000    4724000000    3495000000
19       2006-09-30              USD    5598000000   19315000000   13717000000  ...                              None                        None    2453000000    2678000000    1989000000

[20 rows x 26 columns], 'AAPL')
```

## `get_income_statement_quarterly`

Sample output:

```python
(   fiscalDateEnding reportedCurrency  grossProfit  totalRevenue costOfRevenue  ... netIncomeFromContinuingOperations comprehensiveIncomeNetOfTax         ebit       ebitda    netIncome
0        2025-09-30              USD  48341000000  102466000000   54125000000  ...                       27466000000                        None  32804000000  35931000000  27466000000  
1        2025-06-30              USD  43718000000   94036000000   50318000000  ...                       23434000000                        None  28202000000  31032000000  23434000000  
2        2025-03-31              USD  44867000000   95359000000   50492000000  ...                       24780000000                        None  29589000000  32250000000  24780000000  
3        2024-12-31              USD  58275000000  124300000000   66025000000  ...                       36330000000                        None  42832000000  45912000000  36330000000  
4        2024-09-30              USD  43879000000   94930000000   51051000000  ...                       14736000000                        None  29591000000  32502000000  14736000000  
..              ...              ...          ...           ...           ...  ...                               ...                         ...          ...          ...          ...  
76       2006-09-30              USD   1412000000    4370000000    3425000000  ...                                 0                        None    661000000    718000000    542000000  
77       2006-06-30              USD   1325000000    4370000000    3045000000  ...                                 0                        None    566000000    623000000    472000000  
78       2006-03-31              USD   1297000000    4359000000    3062000000  ...                                 0                        None    529000000    579000000    410000000  
79       2005-12-31              USD   1564000000    5749000000    4185000000  ...                                 0                        None    750000000    802000000    565000000  
80       2005-09-30              USD   1035000000    3678000000    2643000000  ...                                 0                        None    418000000    469000000    430000000  

[81 rows x 26 columns], 'AAPL')
```

## `get_splits`

Sample output:

```python
(  effective_date split_factor
0     2020-08-31       4.0000
1     2014-06-09       7.0000
2     2005-02-28       2.0000
3     2000-06-21       2.0000, 'AAPL')
```
---

Notes:

- All samples are truncated for brevity. Use the official Finnhub endpoints to retrieve full results.
- Values and timestamps in these examples are illustrative and may change over time.

