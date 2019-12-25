from ToolBox.DataBaseFun.DataBase import *
import pandas as pd


def get_opt_min_data(code, date):
    SQL = "SELECT * FROM MIN_DATA WHERE SecurityID='{0}' and date(DTime)='{1}'".format(code, date)
    df = pd.read_sql(SQL, Trading_CONN)
    df = df.set_index('DTime')
    return df


def get_etf_min_data(date):
    SQL = "SELECT * FROM ETF_MIN_DATA where day(DATE)={0}".format(date)
    df = pd.read_sql(SQL, Trading_CONN)
    df = df.set_index('DTime')
    return df


def get_backtest_time_line(start_date, end_date):
    SQL = "SELECT DISTINCT DATE(DTime) FROM ETF_MIN_DATA" \
          " WHERE DTime BETWEEN '{0}' AND '{1}'".format(start_date, end_date)
    df = pd.read_sql(SQL, Trading_CONN)
    return df.values.T[0]

def get_opt_code(level, is_call, is_this_month, time_spot=None): # C++ 合约设置需要处理
    if isinstance(time_spot, pd.Timestamp):
        time_spot = str(time_spot)
    SQL = "SELECT sClose FROM ETF_MIN_DATA WHERE DTime='{0}'".format(str(time_spot))
    etf_price = pd.read_sql(SQL, Trading_CONN).values[0][0]
    date = str(time_spot)[:10]
    SQL2 = "SELECT SecurityID, Strike FROM HIST_OPT_INST " \
               "WHERE DTime='{0}' AND Month={1} AND IsCall={2}".format(date, is_this_month, is_call)
    data = pd.read_sql(SQL2, Trading_CONN)
    data['distance'] = data['Strike'] - etf_price
    if is_call:
        code, strike = data[data['distance'] >= 0].sort_values('distance').iloc[level, [0,1]]
    else:
        code, strike = data[data['distance'] <= 0].sort_values('distance', ascending=False).iloc[level, [0,1]]
    return code, strike


if __name__ == "__main__":
    time = get_backtest_time_line("2019-01-01","2019-12-25")
    df = get_opt_min_data("10001908", "2019-12-20")
    x = get_opt_code(1,0,0,"2019-12-20 09:30:00")
