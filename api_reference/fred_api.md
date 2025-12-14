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

## `get_series_vintage_dates("CPIAUCSL")`

Sample output (panda dataframe):

```json
[datetime.datetime(1972, 7, 21, 0, 0), datetime.datetime(1972, 8, 22, 0, 0), datetime.datetime(1972, 9, 22, 0, 0), datetime.datetime(1972, 10, 20, 0, 0), datetime.datetime(1972, 11, 21, 0, 0), datetime.datetime(1972, 12, 22, 0, 0), datetime.datetime(1973, 1, 23, 0, 0), datetime.datetime(1973, 2, 22, 0, 0), datetime.datetime(1973, 3, 21, 0, 0), datetime.datetime(1973, 4, 20, 0, 0), datetime.datetime(1973, 5, 22, 0, 0), datetime.datetime(1973, 6, 21, 0, 0), datetime.datetime(1973, 7, 20, 0, 0), datetime.datetime(1973, 8, 21, 0, 0), datetime.datetime(1973, 9, 21, 0, 0), datetime.datetime(1973, 10, 19, 0, 0), datetime.datetime(1973, 11, 21, 0, 0), datetime.datetime(1973, 12, 21, 0, 0), datetime.datetime(1974, 1, 22, 0, 0), datetime.datetime(1974, 2, 22, 0, 0), datetime.datetime(1974, 3, 21, 0, 0), datetime.datetime(1974, 4, 19, 0, 0), datetime.datetime(1974, 5, 21, 0, 0), datetime.datetime(1974, 6, 21, 0, 0), datetime.datetime(1974, 7, 19, 0, 0), datetime.datetime(1974, 8, 21, 0, 0), datetime.datetime(1974, 9, 20, 0, 0), datetime.datetime(1974, 10, 22, 0, 0), datetime.datetime(1974, 11, 21, 0, 0), datetime.datetime(1974, 12, 20, 0, 0), datetime.datetime(1975, 1, 21, 0, 
0), datetime.datetime(1975, 2, 21, 0, 0), datetime.datetime(1975, 3, 20, 0, 0), datetime.datetime(1975, 4, 22, 0, 0), datetime.datetime(1975, 5, 21, 0, 0), datetime.datetime(1975, 6, 20, 0, 0), datetime.datetime(1975, 7, 22, 0, 0), datetime.datetime(1975, 8, 21, 0, 0), datetime.datetime(1975, 9, 19, 0, 0), datetime.datetime(1975, 10, 22, 0, 0), datetime.datetime(1975, 11, 20, 0, 0), datetime.datetime(1975, 12, 19, 0, 0), datetime.datetime(1976, 1, 21, 0, 0), datetime.datetime(1976, 2, 20, 0, 0), datetime.datetime(1976, 3, 19, 0, 0), datetime.datetime(1976, 4, 21, 0, 0), datetime.datetime(1976, 5, 21, 0, 0), datetime.datetime(1976, 6, 22, 0, 0), datetime.datetime(1976, 7, 21, 0, 0), datetime.datetime(1976, 8, 20, 0, 0), datetime.datetime(1976, 9, 21, 0, 0), datetime.datetime(1976, 10, 21, 0, 0), datetime.datetime(1976, 11, 19, 0, 0), datetime.datetime(1976, 12, 21, 0, 0), datetime.datetime(1977, 1, 19, 0, 0), datetime.datetime(1977, 2, 18, 0, 0), datetime.datetime(1977, 3, 18, 0, 0), datetime.datetime(1977, 4, 21, 0, 0), 
datetime.datetime(1977, 5, 20, 0, 0), datetime.datetime(1977, 6, 21, 0, 0), datetime.datetime(1977, 7, 21, 0, 0), datetime.datetime(1977, 8, 19, 0, 
0), datetime.datetime(1977, 9, 21, 0, 0), datetime.datetime(1977, 10, 21, 0, 0), datetime.datetime(1977, 11, 22, 0, 0), datetime.datetime(1977, 12, 
21, 0, 0), datetime.datetime(1978, 1, 20, 0, 0), datetime.datetime(1978, 2, 27, 0, 0), datetime.datetime(1978, 3, 28, 0, 0), datetime.datetime(1978, 4, 28, 0, 0), datetime.datetime(1978, 5, 31, 0, 0), datetime.datetime(1978, 6, 30, 0, 0), datetime.datetime(1978, 7, 28, 0, 0), datetime.datetime(1978, 8, 29, 0, 0), datetime.datetime(1978, 9, 26, 0, 0), datetime.datetime(1978, 10, 26, 0, 0), datetime.datetime(1978, 11, 28, 0, 0), datetime.datetime(1978, 12, 22, 0, 0), datetime.datetime(1979, 1, 24, 0, 0), datetime.datetime(1979, 2, 23, 0, 0), datetime.datetime(1979, 3, 23, 0, 0), datetime.datetime(1979, 4, 26, 0, 0), datetime.datetime(1979, 5, 25, 0, 0), datetime.datetime(1979, 6, 26, 0, 0), datetime.datetime(1979, 7, 26, 0, 0), datetime.datetime(1979, 8, 24, 0, 0), datetime.datetime(1979, 9, 25, 0, 0), datetime.datetime(1979, 10, 26, 0, 0), datetime.datetime(1979, 11, 27, 0, 0), datetime.datetime(1979, 12, 21, 0, 0), datetime.datetime(1980, 1, 25, 0, 0), datetime.datetime(1980, 2, 22, 0, 0), datetime.datetime(1980, 3, 25, 
0, 0), datetime.datetime(1980, 4, 22, 0, 0), datetime.datetime(1980, 5, 23, 0, 0), datetime.datetime(1980, 6, 24, 0, 0), datetime.datetime(1980, 7, 
23, 0, 0), datetime.datetime(1980, 8, 22, 0, 0), datetime.datetime(1980, 9, 23, 0, 0), datetime.datetime(1980, 10, 24, 0, 0), datetime.datetime(1980, 11, 25, 0, 0), datetime.datetime(1980, 12, 23, 0, 0), datetime.datetime(1981, 1, 23, 0, 0), datetime.datetime(1981, 2, 25, 0, 0), datetime.datetime(1981, 3, 24, 0, 0), datetime.datetime(1981, 4, 23, 0, 0), datetime.datetime(1981, 5, 22, 0, 0), datetime.datetime(1981, 6, 23, 0, 0), datetime.datetime(1981, 7, 23, 0, 0), datetime.datetime(1981, 8, 25, 0, 0), datetime.datetime(1981, 9, 24, 0, 0), datetime.datetime(1981, 10, 23, 0, 0), datetime.datetime(1981, 11, 24, 0, 0), datetime.datetime(1981, 12, 22, 0, 0), datetime.datetime(1982, 1, 22, 0, 0), datetime.datetime(1982, 2, 25, 0, 0), datetime.datetime(1982, 3, 23, 0, 0), datetime.datetime(1982, 4, 23, 0, 0), datetime.datetime(1982, 5, 21, 0, 0), datetime.datetime(1982, 6, 22, 0, 0), datetime.datetime(1982, 7, 23, 0, 0), datetime.datetime(1982, 8, 24, 0, 0), datetime.datetime(1982, 9, 23, 0, 0), datetime.datetime(1982, 10, 26, 0, 0), datetime.datetime(1982, 11, 23, 0, 0), datetime.datetime(1982, 12, 21, 0, 0), datetime.datetime(1983, 1, 21, 0, 0), datetime.datetime(1983, 
2, 25, 0, 0), datetime.datetime(1983, 3, 23, 0, 0), datetime.datetime(1983, 4, 22, 0, 0), datetime.datetime(1983, 5, 24, 0, 0), datetime.datetime(1983, 6, 22, 0, 0), datetime.datetime(1983, 7, 22, 0, 0), datetime.datetime(1983, 8, 23, 0, 0), datetime.datetime(1983, 9, 23, 0, 0), datetime.datetime(1983, 10, 25, 0, 0), datetime.datetime(1983, 11, 23, 0, 0), datetime.datetime(1983, 12, 21, 0, 0), datetime.datetime(1984, 1, 24, 0, 0), datetime.datetime(1984, 2, 24, 0, 0), datetime.datetime(1984, 3, 23, 0, 0), datetime.datetime(1984, 4, 24, 0, 0), datetime.datetime(1984, 5, 22, 0, 0), datetime.datetime(1984, 6, 22, 0, 0), datetime.datetime(1984, 7, 24, 0, 0), datetime.datetime(1984, 8, 22, 0, 0), datetime.datetime(1984, 9, 21, 0, 0), datetime.datetime(1984, 10, 24, 0, 0), datetime.datetime(1984, 11, 21, 0, 0), datetime.datetime(1984, 12, 20, 0, 0), datetime.datetime(1985, 1, 23, 0, 0), datetime.datetime(1985, 2, 26, 0, 0), datetime.datetime(1985, 3, 22, 0, 0), datetime.datetime(1985, 4, 23, 0, 0), datetime.datetime(1985, 5, 21, 0, 0), datetime.datetime(1985, 6, 20, 0, 0), datetime.datetime(1985, 7, 23, 0, 0), datetime.datetime(1985, 8, 22, 0, 0), datetime.datetime(1985, 
9, 24, 0, 0), datetime.datetime(1985, 10, 23, 0, 0), datetime.datetime(1985, 11, 22, 0, 0), datetime.datetime(1985, 12, 20, 0, 0), datetime.datetime(1986, 1, 22, 0, 0), datetime.datetime(1986, 2, 25, 0, 0), datetime.datetime(1986, 3, 25, 0, 0), datetime.datetime(1986, 4, 22, 0, 0), datetime.datetime(1986, 5, 21, 0, 0), datetime.datetime(1986, 6, 20, 0, 0), datetime.datetime(1986, 7, 23, 0, 0), datetime.datetime(1986, 8, 21, 0, 0), datetime.datetime(1986, 9, 23, 0, 0), datetime.datetime(1986, 10, 23, 0, 0), datetime.datetime(1986, 11, 25, 0, 0), datetime.datetime(1986, 12, 19, 0, 0), datetime.datetime(1987, 1, 21, 0, 0), datetime.datetime(1987, 2, 27, 0, 0), datetime.datetime(1987, 3, 27, 0, 0), datetime.datetime(1987, 4, 24, 0, 0), datetime.datetime(1987, 5, 22, 0, 0), datetime.datetime(1987, 6, 23, 0, 0), datetime.datetime(1987, 7, 22, 0, 0), datetime.datetime(1987, 8, 21, 0, 0), datetime.datetime(1987, 9, 23, 0, 0), datetime.datetime(1987, 10, 23, 0, 0), datetime.datetime(1987, 11, 20, 0, 0), datetime.datetime(1987, 12, 18, 0, 0), datetime.datetime(1988, 1, 20, 0, 0), datetime.datetime(1988, 2, 26, 0, 0), datetime.datetime(1988, 3, 23, 0, 0), datetime.datetime(1988, 4, 20, 0, 0), datetime.datetime(1988, 5, 20, 0, 0), datetime.datetime(1988, 6, 21, 0, 0), datetime.datetime(1988, 7, 22, 0, 0), datetime.datetime(1988, 8, 23, 0, 0), datetime.datetime(1988, 9, 21, 0, 0), datetime.datetime(1988, 10, 21, 0, 0), datetime.datetime(1988, 11, 22, 0, 0), datetime.datetime(1988, 12, 20, 0, 0), datetime.datetime(1989, 1, 19, 0, 0), datetime.datetime(1989, 2, 22, 0, 0), datetime.datetime(1989, 3, 21, 0, 0), datetime.datetime(1989, 4, 18, 0, 0), datetime.datetime(1989, 5, 18, 0, 0), datetime.datetime(1989, 6, 16, 0, 0), datetime.datetime(1989, 7, 19, 0, 0), datetime.datetime(1989, 8, 18, 0, 0), datetime.datetime(1989, 9, 19, 0, 0), datetime.datetime(1989, 10, 19, 0, 0), datetime.datetime(1989, 11, 21, 0, 
0), datetime.datetime(1989, 12, 19, 0, 0), datetime.datetime(1990, 1, 18, 0, 0), datetime.datetime(1990, 2, 21, 0, 0), datetime.datetime(1990, 3, 20, 0, 0), datetime.datetime(1990, 4, 17, 0, 0), datetime.datetime(1990, 5, 16, 0, 0), datetime.datetime(1990, 6, 15, 0, 0), datetime.datetime(1990, 7, 18, 0, 0), datetime.datetime(1990, 8, 16, 0, 0), datetime.datetime(1990, 9, 18, 0, 0), datetime.datetime(1990, 10, 18, 0, 0), datetime.datetime(1990, 11, 16, 0, 0), datetime.datetime(1990, 12, 18, 0, 0), datetime.datetime(1991, 1, 16, 0, 0), datetime.datetime(1991, 2, 20, 0, 0), datetime.datetime(1991, 3, 19, 0, 0), datetime.datetime(1991, 4, 12, 0, 0), datetime.datetime(1991, 5, 14, 0, 0), datetime.datetime(1991, 6, 14, 0, 0), datetime.datetime(1991, 7, 17, 0, 0), datetime.datetime(1991, 8, 14, 0, 0), datetime.datetime(1991, 9, 13, 0, 0), datetime.datetime(1991, 10, 17, 0, 0), datetime.datetime(1991, 11, 14, 0, 0), datetime.datetime(1991, 12, 13, 0, 0), datetime.datetime(1992, 1, 16, 0, 0), datetime.datetime(1992, 2, 19, 0, 0), datetime.datetime(1992, 3, 17, 0, 0), datetime.datetime(1992, 4, 10, 0, 0), datetime.datetime(1992, 5, 13, 0, 0), datetime.datetime(1992, 6, 12, 0, 0), datetime.datetime(1992, 7, 14, 0, 0), datetime.datetime(1992, 8, 13, 0, 0), datetime.datetime(1992, 9, 15, 0, 0), datetime.datetime(1992, 10, 15, 0, 0), datetime.datetime(1992, 11, 13, 0, 0), datetime.datetime(1992, 12, 13, 0, 0), datetime.datetime(1993, 1, 15, 0, 0), datetime.datetime(1993, 2, 18, 0, 0), datetime.datetime(1993, 3, 17, 0, 0), datetime.datetime(1993, 4, 9, 0, 0), datetime.datetime(1993, 5, 13, 0, 0), datetime.datetime(1993, 6, 15, 0, 0), datetime.datetime(1993, 7, 14, 0, 0), datetime.datetime(1993, 8, 13, 0, 0), datetime.datetime(1993, 9, 14, 0, 0), datetime.datetime(1993, 10, 15, 0, 0), datetime.datetime(1993, 11, 10, 0, 0), datetime.datetime(1993, 12, 10, 0, 0), datetime.datetime(1994, 1, 13, 0, 0), datetime.datetime(1994, 2, 17, 0, 0), datetime.datetime(1994, 3, 16, 0, 0), datetime.datetime(1994, 4, 13, 0, 0), datetime.datetime(1994, 5, 13, 0, 0), datetime.datetime(1994, 6, 14, 0, 0), datetime.datetime(1994, 7, 13, 0, 0), datetime.datetime(1994, 8, 12, 0, 0), datetime.datetime(1994, 9, 13, 0, 0), 
datetime.datetime(1994, 10, 14, 0, 0), datetime.datetime(1994, 11, 16, 0, 0), datetime.datetime(1994, 12, 14, 0, 0), datetime.datetime(1995, 1, 11, 
0, 0), datetime.datetime(1995, 2, 15, 0, 0), datetime.datetime(1995, 3, 16, 0, 0), datetime.datetime(1995, 4, 12, 0, 0), datetime.datetime(1995, 5, 
12, 0, 0), datetime.datetime(1995, 6, 13, 0, 0), datetime.datetime(1995, 7, 14, 0, 0), datetime.datetime(1995, 8, 11, 0, 0), datetime.datetime(1995, 9, 13, 0, 0), datetime.datetime(1995, 10, 13, 0, 0), datetime.datetime(1995, 11, 15, 0, 0), datetime.datetime(1995, 12, 14, 0, 0), datetime.datetime(1996, 2, 1, 0, 0), datetime.datetime(1996, 2, 28, 0, 0), datetime.datetime(1996, 3, 15, 0, 0), datetime.datetime(1996, 4, 12, 0, 0), datetime.datetime(1996, 5, 14, 0, 0), datetime.datetime(1996, 6, 12, 0, 0), datetime.datetime(1996, 7, 16, 0, 0), datetime.datetime(1996, 8, 13, 0, 0), datetime.datetime(1996, 9, 13, 0, 0), datetime.datetime(1996, 10, 16, 0, 0), datetime.datetime(1996, 11, 14, 0, 0), datetime.datetime(1996, 12, 12, 0, 0), datetime.datetime(1997, 1, 14, 0, 0), datetime.datetime(1997, 2, 19, 0, 0), datetime.datetime(1997, 3, 19, 0, 0), datetime.datetime(1997, 4, 15, 0, 0), datetime.datetime(1997, 5, 15, 0, 0), datetime.datetime(1997, 6, 17, 0, 0), datetime.datetime(1997, 7, 16, 0, 0), datetime.datetime(1997, 8, 14, 0, 0), datetime.datetime(1997, 9, 16, 0, 0), datetime.datetime(1997, 10, 16, 0, 0), datetime.datetime(1997, 11, 18, 0, 0), datetime.datetime(1997, 12, 16, 0, 0), datetime.datetime(1998, 1, 13, 0, 0), datetime.datetime(1998, 2, 24, 0, 0), datetime.datetime(1998, 3, 19, 0, 0), datetime.datetime(1998, 4, 14, 0, 0), datetime.datetime(1998, 5, 14, 0, 0), datetime.datetime(1998, 6, 16, 0, 0), datetime.datetime(1998, 7, 14, 0, 0), datetime.datetime(1998, 8, 18, 0, 0), datetime.datetime(1998, 9, 17, 0, 0), datetime.datetime(1998, 10, 16, 0, 0), datetime.datetime(1998, 11, 17, 0, 0), datetime.datetime(1998, 12, 15, 0, 0), datetime.datetime(1999, 1, 14, 0, 0), datetime.datetime(1999, 2, 19, 0, 0), datetime.datetime(1999, 3, 18, 0, 0), datetime.datetime(1999, 4, 13, 0, 0), datetime.datetime(1999, 5, 14, 0, 0), datetime.datetime(1999, 6, 16, 0, 0), datetime.datetime(1999, 7, 15, 0, 0), datetime.datetime(1999, 8, 17, 0, 0), datetime.datetime(1999, 9, 15, 0, 0), datetime.datetime(1999, 10, 19, 0, 0), datetime.datetime(1999, 11, 17, 0, 
0), datetime.datetime(1999, 12, 14, 0, 0), datetime.datetime(2000, 1, 14, 0, 0), datetime.datetime(2000, 2, 18, 0, 0), datetime.datetime(2000, 3, 17, 0, 0), datetime.datetime(2000, 4, 14, 0, 0), datetime.datetime(2000, 5, 16, 0, 0), datetime.datetime(2000, 6, 14, 0, 0), datetime.datetime(2000, 7, 18, 0, 0), datetime.datetime(2000, 8, 16, 0, 0), datetime.datetime(2000, 9, 15, 0, 0), datetime.datetime(2000, 9, 28, 0, 0), datetime.datetime(2000, 10, 18, 0, 0), datetime.datetime(2000, 11, 16, 0, 0), datetime.datetime(2000, 12, 15, 0, 0), datetime.datetime(2001, 1, 17, 0, 0), datetime.datetime(2001, 2, 21, 0, 0), datetime.datetime(2001, 3, 21, 0, 0), datetime.datetime(2001, 4, 17, 0, 0), datetime.datetime(2001, 5, 16, 0, 0), datetime.datetime(2001, 6, 15, 0, 0), datetime.datetime(2001, 7, 18, 0, 0), datetime.datetime(2001, 8, 16, 0, 0), datetime.datetime(2001, 9, 18, 0, 0), datetime.datetime(2001, 10, 19, 0, 0), datetime.datetime(2001, 11, 16, 0, 0), datetime.datetime(2001, 12, 14, 0, 0), datetime.datetime(2002, 1, 16, 0, 0), datetime.datetime(2002, 2, 20, 0, 0), datetime.datetime(2002, 3, 21, 0, 0), datetime.datetime(2002, 4, 16, 0, 0), datetime.datetime(2002, 5, 15, 0, 0), datetime.datetime(2002, 6, 18, 0, 0), datetime.datetime(2002, 7, 19, 0, 0), datetime.datetime(2002, 8, 16, 0, 0), datetime.datetime(2002, 9, 18, 0, 0), datetime.datetime(2002, 10, 18, 0, 0), datetime.datetime(2002, 11, 19, 0, 0), datetime.datetime(2002, 12, 17, 0, 0), datetime.datetime(2003, 1, 16, 0, 0), datetime.datetime(2003, 2, 21, 0, 0), datetime.datetime(2003, 3, 21, 0, 0), datetime.datetime(2003, 4, 16, 0, 0), datetime.datetime(2003, 5, 16, 0, 0), datetime.datetime(2003, 6, 17, 0, 0), datetime.datetime(2003, 7, 16, 0, 0), datetime.datetime(2003, 8, 15, 0, 0), datetime.datetime(2003, 9, 16, 0, 0), datetime.datetime(2003, 10, 16, 0, 0), datetime.datetime(2003, 11, 18, 0, 0), datetime.datetime(2003, 12, 16, 0, 0), datetime.datetime(2004, 1, 15, 0, 0), datetime.datetime(2004, 2, 20, 0, 0), datetime.datetime(2004, 3, 17, 0, 0), datetime.datetime(2004, 4, 14, 0, 0), datetime.datetime(2004, 5, 14, 0, 0), datetime.datetime(2004, 6, 15, 0, 0), datetime.datetime(2004, 7, 16, 0, 0), datetime.datetime(2004, 8, 17, 0, 0), datetime.datetime(2004, 9, 16, 0, 0), datetime.datetime(2004, 10, 19, 0, 0), datetime.datetime(2004, 11, 17, 0, 0), datetime.datetime(2004, 12, 17, 0, 0), datetime.datetime(2005, 1, 19, 0, 0), datetime.datetime(2005, 2, 18, 0, 0), datetime.datetime(2005, 2, 23, 0, 0), datetime.datetime(2005, 3, 23, 0, 0), datetime.datetime(2005, 4, 20, 0, 0), datetime.datetime(2005, 5, 18, 0, 0), datetime.datetime(2005, 6, 15, 0, 0), datetime.datetime(2005, 7, 14, 0, 0), datetime.datetime(2005, 8, 16, 0, 0), datetime.datetime(2005, 9, 15, 0, 0), datetime.datetime(2005, 10, 14, 0, 0), datetime.datetime(2005, 11, 16, 0, 0), datetime.datetime(2005, 12, 15, 0, 0), datetime.datetime(2006, 1, 18, 0, 0), datetime.datetime(2006, 2, 17, 0, 0), datetime.datetime(2006, 2, 22, 0, 0), datetime.datetime(2006, 3, 16, 0, 0), datetime.datetime(2006, 4, 19, 0, 0), datetime.datetime(2006, 5, 17, 0, 0), datetime.datetime(2006, 6, 14, 0, 0), datetime.datetime(2006, 7, 19, 0, 0), datetime.datetime(2006, 8, 16, 0, 0), datetime.datetime(2006, 9, 15, 0, 0), datetime.datetime(2006, 10, 18, 0, 0), datetime.datetime(2006, 11, 16, 0, 0), datetime.datetime(2006, 12, 15, 0, 0), datetime.datetime(2007, 1, 18, 0, 
0), datetime.datetime(2007, 2, 16, 0, 0), datetime.datetime(2007, 2, 21, 0, 0), datetime.datetime(2007, 3, 16, 0, 0), datetime.datetime(2007, 4, 17, 0, 0), datetime.datetime(2007, 5, 15, 0, 0), datetime.datetime(2007, 6, 15, 0, 0), datetime.datetime(2007, 7, 18, 0, 0), datetime.datetime(2007, 8, 15, 0, 0), datetime.datetime(2007, 9, 19, 0, 0), datetime.datetime(2007, 10, 17, 0, 0), datetime.datetime(2007, 11, 15, 0, 0), datetime.datetime(2007, 12, 14, 0, 0), datetime.datetime(2008, 1, 16, 0, 0), datetime.datetime(2008, 2, 15, 0, 0), datetime.datetime(2008, 2, 20, 0, 0), datetime.datetime(2008, 3, 14, 0, 0), datetime.datetime(2008, 4, 16, 0, 0), datetime.datetime(2008, 5, 14, 0, 0), datetime.datetime(2008, 6, 13, 0, 0), datetime.datetime(2008, 7, 16, 0, 0), datetime.datetime(2008, 8, 14, 0, 0), datetime.datetime(2008, 9, 16, 0, 0), datetime.datetime(2008, 10, 16, 0, 0), datetime.datetime(2008, 11, 19, 0, 0), datetime.datetime(2008, 12, 16, 0, 0), datetime.datetime(2009, 1, 16, 0, 0), datetime.datetime(2009, 2, 18, 0, 0), 
datetime.datetime(2009, 2, 20, 0, 0), datetime.datetime(2009, 3, 18, 0, 0), datetime.datetime(2009, 4, 15, 0, 0), datetime.datetime(2009, 5, 15, 0, 
0), datetime.datetime(2009, 6, 17, 0, 0), datetime.datetime(2009, 7, 15, 0, 0), datetime.datetime(2009, 8, 14, 0, 0), datetime.datetime(2009, 9, 16, 0, 0), datetime.datetime(2009, 10, 15, 0, 0), datetime.datetime(2009, 11, 18, 0, 0), datetime.datetime(2009, 12, 16, 0, 0), datetime.datetime(2010, 1, 15, 0, 0), datetime.datetime(2010, 2, 17, 0, 0), datetime.datetime(2010, 2, 19, 0, 0), datetime.datetime(2010, 3, 18, 0, 0), datetime.datetime(2010, 4, 14, 0, 0), datetime.datetime(2010, 5, 19, 0, 0), datetime.datetime(2010, 6, 17, 0, 0), datetime.datetime(2010, 7, 16, 0, 0), datetime.datetime(2010, 8, 13, 0, 0), datetime.datetime(2010, 9, 17, 0, 0), datetime.datetime(2010, 10, 15, 0, 0), datetime.datetime(2010, 11, 17, 0, 0), datetime.datetime(2010, 12, 15, 0, 0), datetime.datetime(2011, 1, 14, 0, 0), datetime.datetime(2011, 2, 15, 0, 0), datetime.datetime(2011, 2, 17, 0, 0), datetime.datetime(2011, 3, 17, 0, 0), datetime.datetime(2011, 4, 15, 0, 0), datetime.datetime(2011, 5, 13, 0, 0), datetime.datetime(2011, 6, 15, 0, 0), 
datetime.datetime(2011, 7, 15, 0, 0), datetime.datetime(2011, 8, 18, 0, 0), datetime.datetime(2011, 9, 15, 0, 0), datetime.datetime(2011, 10, 19, 0, 0), datetime.datetime(2011, 11, 16, 0, 0), datetime.datetime(2011, 12, 16, 0, 0), datetime.datetime(2012, 1, 19, 0, 0), datetime.datetime(2012, 2, 
15, 0, 0), datetime.datetime(2012, 2, 17, 0, 0), datetime.datetime(2012, 3, 16, 0, 0), datetime.datetime(2012, 4, 13, 0, 0), datetime.datetime(2012, 5, 15, 0, 0), datetime.datetime(2012, 6, 14, 0, 0), datetime.datetime(2012, 7, 17, 0, 0), datetime.datetime(2012, 8, 15, 0, 0), datetime.datetime(2012, 9, 14, 0, 0), datetime.datetime(2012, 10, 16, 0, 0), datetime.datetime(2012, 11, 15, 0, 0), datetime.datetime(2012, 12, 14, 0, 0), datetime.datetime(2013, 1, 16, 0, 0), datetime.datetime(2013, 2, 19, 0, 0), datetime.datetime(2013, 2, 21, 0, 0), datetime.datetime(2013, 3, 15, 0, 0), datetime.datetime(2013, 4, 16, 0, 0), datetime.datetime(2013, 5, 16, 0, 0), datetime.datetime(2013, 6, 18, 0, 0), datetime.datetime(2013, 7, 16, 0, 0), datetime.datetime(2013, 8, 15, 0, 0), datetime.datetime(2013, 9, 17, 0, 0), datetime.datetime(2013, 10, 30, 0, 0), datetime.datetime(2013, 11, 20, 0, 0), datetime.datetime(2013, 12, 17, 0, 0), datetime.datetime(2014, 1, 16, 0, 0), datetime.datetime(2014, 2, 18, 0, 0), datetime.datetime(2014, 2, 20, 
0, 0), datetime.datetime(2014, 3, 18, 0, 0), datetime.datetime(2014, 4, 15, 0, 0), datetime.datetime(2014, 5, 15, 0, 0), datetime.datetime(2014, 6, 
17, 0, 0), datetime.datetime(2014, 7, 22, 0, 0), datetime.datetime(2014, 8, 19, 0, 0), datetime.datetime(2014, 9, 17, 0, 0), datetime.datetime(2014, 10, 22, 0, 0), datetime.datetime(2014, 11, 20, 0, 0), datetime.datetime(2014, 12, 17, 0, 0), datetime.datetime(2015, 1, 16, 0, 0), datetime.datetime(2015, 2, 20, 0, 0), datetime.datetime(2015, 2, 26, 0, 0), datetime.datetime(2015, 3, 24, 0, 0), datetime.datetime(2015, 4, 17, 0, 0), datetime.datetime(2015, 5, 22, 0, 0), datetime.datetime(2015, 6, 18, 0, 0), datetime.datetime(2015, 7, 17, 0, 0), datetime.datetime(2015, 8, 19, 0, 0), datetime.datetime(2015, 9, 16, 0, 0), datetime.datetime(2015, 10, 15, 0, 0), datetime.datetime(2015, 11, 17, 0, 0), datetime.datetime(2015, 12, 15, 0, 0), datetime.datetime(2016, 1, 20, 0, 0), datetime.datetime(2016, 2, 19, 0, 0), datetime.datetime(2016, 3, 16, 0, 0), datetime.datetime(2016, 4, 14, 0, 0), datetime.datetime(2016, 5, 17, 0, 0), datetime.datetime(2016, 6, 16, 0, 0), datetime.datetime(2016, 7, 15, 0, 0), datetime.datetime(2016, 8, 16, 
0, 0), datetime.datetime(2016, 9, 16, 0, 0), datetime.datetime(2016, 10, 18, 0, 0), datetime.datetime(2016, 11, 17, 0, 0), datetime.datetime(2016, 12, 15, 0, 0), datetime.datetime(2017, 1, 18, 0, 0), datetime.datetime(2017, 2, 13, 0, 0), datetime.datetime(2017, 2, 15, 0, 0), datetime.datetime(2017, 3, 15, 0, 0), datetime.datetime(2017, 4, 14, 0, 0), datetime.datetime(2017, 5, 12, 0, 0), datetime.datetime(2017, 6, 14, 0, 0), datetime.datetime(2017, 7, 14, 0, 0), datetime.datetime(2017, 8, 11, 0, 0), datetime.datetime(2017, 9, 14, 0, 0), datetime.datetime(2017, 10, 13, 0, 0), datetime.datetime(2017, 11, 15, 0, 0), datetime.datetime(2017, 12, 13, 0, 0), datetime.datetime(2018, 1, 12, 0, 0), datetime.datetime(2018, 2, 14, 0, 0), datetime.datetime(2018, 3, 13, 0, 0), datetime.datetime(2018, 4, 11, 0, 0), datetime.datetime(2018, 5, 10, 0, 0), datetime.datetime(2018, 6, 12, 0, 0), datetime.datetime(2018, 7, 12, 0, 0), datetime.datetime(2018, 8, 10, 0, 0), datetime.datetime(2018, 9, 13, 0, 0), datetime.datetime(2018, 10, 11, 0, 
0), datetime.datetime(2018, 11, 14, 0, 0), datetime.datetime(2018, 12, 12, 0, 0), datetime.datetime(2019, 1, 11, 0, 0), datetime.datetime(2019, 2, 11, 0, 0), datetime.datetime(2019, 2, 13, 0, 0), datetime.datetime(2019, 3, 12, 0, 0), datetime.datetime(2019, 4, 10, 0, 0), datetime.datetime(2019, 
5, 10, 0, 0), datetime.datetime(2019, 6, 12, 0, 0), datetime.datetime(2019, 7, 11, 0, 0), datetime.datetime(2019, 8, 13, 0, 0), datetime.datetime(2019, 9, 12, 0, 0), datetime.datetime(2019, 10, 10, 0, 0), datetime.datetime(2019, 11, 13, 0, 0), datetime.datetime(2019, 12, 11, 0, 0), datetime.datetime(2020, 1, 14, 0, 0), datetime.datetime(2020, 2, 11, 0, 0), datetime.datetime(2020, 2, 13, 0, 0), datetime.datetime(2020, 3, 11, 0, 0), datetime.datetime(2020, 4, 10, 0, 0), datetime.datetime(2020, 5, 12, 0, 0), datetime.datetime(2020, 6, 10, 0, 0), datetime.datetime(2020, 7, 14, 0, 0), datetime.datetime(2020, 8, 12, 0, 0), datetime.datetime(2020, 9, 11, 0, 0), datetime.datetime(2020, 10, 13, 0, 0), datetime.datetime(2020, 11, 12, 0, 0), datetime.datetime(2020, 12, 10, 0, 0), datetime.datetime(2021, 1, 13, 0, 0), datetime.datetime(2021, 2, 8, 0, 0), datetime.datetime(2021, 2, 10, 0, 0), datetime.datetime(2021, 3, 10, 0, 0), datetime.datetime(2021, 4, 13, 0, 0), datetime.datetime(2021, 5, 12, 0, 0), datetime.datetime(2021, 6, 10, 0, 0), datetime.datetime(2021, 7, 13, 0, 0), datetime.datetime(2021, 8, 11, 0, 0), datetime.datetime(2021, 9, 14, 0, 0), datetime.datetime(2021, 10, 13, 0, 0), datetime.datetime(2021, 11, 10, 0, 0), datetime.datetime(2021, 12, 10, 0, 0), datetime.datetime(2022, 1, 12, 0, 0), datetime.datetime(2022, 2, 8, 0, 0), datetime.datetime(2022, 2, 10, 0, 0), datetime.datetime(2022, 3, 10, 0, 0), datetime.datetime(2022, 4, 12, 0, 0), datetime.datetime(2022, 5, 11, 0, 0), datetime.datetime(2022, 6, 10, 0, 0), datetime.datetime(2022, 7, 13, 0, 0), datetime.datetime(2022, 8, 10, 0, 0), datetime.datetime(2022, 9, 13, 0, 0), datetime.datetime(2022, 10, 13, 0, 0), datetime.datetime(2022, 11, 10, 0, 0), datetime.datetime(2022, 12, 13, 0, 0), datetime.datetime(2023, 1, 12, 0, 0), datetime.datetime(2023, 2, 10, 0, 0), datetime.datetime(2023, 2, 14, 0, 0), datetime.datetime(2023, 3, 14, 0, 0), 
datetime.datetime(2023, 4, 12, 0, 0), datetime.datetime(2023, 5, 10, 0, 0), datetime.datetime(2023, 6, 13, 0, 0), datetime.datetime(2023, 7, 12, 0, 
0), datetime.datetime(2023, 8, 10, 0, 0), datetime.datetime(2023, 9, 13, 0, 0), datetime.datetime(2023, 10, 12, 0, 0), datetime.datetime(2023, 11, 14, 0, 0), datetime.datetime(2023, 12, 12, 0, 0), datetime.datetime(2024, 1, 11, 0, 0), datetime.datetime(2024, 2, 9, 0, 0), datetime.datetime(2024, 
2, 13, 0, 0), datetime.datetime(2024, 3, 12, 0, 0), datetime.datetime(2024, 4, 10, 0, 0), datetime.datetime(2024, 5, 15, 0, 0), datetime.datetime(2024, 6, 12, 0, 0), datetime.datetime(2024, 7, 11, 0, 0), datetime.datetime(2024, 8, 14, 0, 0), datetime.datetime(2024, 9, 11, 0, 0), datetime.datetime(2024, 10, 10, 0, 0), datetime.datetime(2024, 11, 13, 0, 0), datetime.datetime(2024, 12, 11, 0, 0), datetime.datetime(2025, 1, 15, 0, 0), datetime.datetime(2025, 2, 12, 0, 0), datetime.datetime(2025, 3, 12, 0, 0), datetime.datetime(2025, 4, 10, 0, 0), datetime.datetime(2025, 5, 13, 0, 0), datetime.datetime(2025, 6, 11, 0, 0), datetime.datetime(2025, 7, 15, 0, 0), datetime.datetime(2025, 8, 12, 0, 0), datetime.datetime(2025, 9, 11, 0, 0), datetime.datetime(2025, 10, 24, 0, 0)]
```
