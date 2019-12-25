import pandas as pd
import numpy as np
import copy
import pymssql
START_DATE = '2016-01-01'
END_DATE = '2019-09-01'
CONN = pymssql.connect(
    "10.0.0.51",
    "sa",
    "abc123",
    "Options"
)
etf_data = pd.read_sql("SELECT * FROM Options.dbo.etfclosedata "
                       "where date between '{0}' and '{1}'".format(START_DATE, END_DATE), CONN, index_col='date')
option_data = pd.read_sql("SELECT * FROM Options.dbo.option_day "
                          "WHERE ddate BETWEEN '{0}' and '{1}'".format(START_DATE, END_DATE), CONN, index_col='ddate')
option_data = option_data.sort_index()


holdings = [0, 0, 0]
holdings_path = []
now_option_month = -1
next_option_month = -1
now_strike = -1

month_holding = []

for i in range(len(etf_data) - 1):
    next_option_month = etf_data.iloc[i + 1, 1]
    if now_option_month != etf_data.iloc[i, 1] or etf_data.index[i].weekday() == 2:
        now_option_month = etf_data.iloc[i, 1]
        today = etf_data.index[i]
        price = etf_data.iloc[i, 0]
        options = option_data[(option_data.index == today) &
                              (option_data['tradecode'].apply(lambda x: x[6]) == 'P') &
                              (option_data['expirydate'].apply(lambda x: x.month) == now_option_month)
                              ]
        options['div'] = abs(options['strike'] - price)
        target_option = options.sort_values('div').iloc[0]
        now_strike = target_option['strike']
        holdings[0] += target_option['sclose']
        month_holding.append(now_strike)
    if next_option_month != now_option_month:  # 到期
        etf_price = etf_data.iloc[i, 0]
        for strike in month_holding:
            if etf_price > strike:
                holdings[1] += 1
                holdings[2] += now_strike
        month_holding = []
    now_option_month = etf_data.iloc[i, 1]
    holdings_path.append(copy.deepcopy(holdings))
