# 这个文件夹中,每个文件都应该能单独执行
import pandas as pd
import datetime
from DataBaseFun.DataBase import *

today = datetime.datetime.today()
today = str(today)[:10]

##todo 这次中秋看看调休的影响


def get_last_trading_day():
    sql = "select distinct date(Dtime) from FUTURE_MIN_DATA"
    df = pd.read_sql(sql, Trading_CONN)
    return str(df.values[-2][0])  # -1 当天 -2 上一个交易日

#today = '2019-07-17'


def get_today_inst():
    SQL = "SELECT SecurityID, ExpiryDays, IsCall, Multiple, Month FROM INST WHERE Month>=0"
    df = pd.read_sql(SQL, Trading_CONN)
    return df

def get_today_future_inst():
    SQL = "select distinct SecurityID from FUTURE_MIN_DATA where date(DTime)='{0}'".format(today)
    df = pd.read_sql(SQL, Trading_CONN)
    return df

def check_today_update(code):
    SQL = "SELECT * FROM DAY_DATA WHERE SecurityID = '{0}' AND DTime='{1}'".format(code, today)
    df = pd.read_sql(SQL, Trading_CONN)
    return df.empty

# 夜盘算第二天

def check_today_future_update(code):
    SQL = "SELECT * FROM FUTURE_DAY_DATA WHERE SecurityID = '{0}' AND DTime='{1}'".format(code, today)
    df = pd.read_sql(SQL, Trading_CONN)
    return df.empty


def update_today_future_data(code):
    if not check_today_future_update(code):
        return
    last_trading_day = get_last_trading_day()
    SQL = "SELECT * FROM FUTURE_MIN_DATA WHERE SecurityID='{0}' AND " \
          "DTime BETWEEN '{1}' AND '{2}'".format(code, last_trading_day + ' 20:30:00', today + ' 15:30:00')
    df = pd.read_sql(SQL, Trading_CONN)
    Open = df.head(1)['sOpen'].values[0]
    Close = df.tail(1)['sClose'].values[0]
    High = df['sHigh'].max()
    Low = df['sLow'].min()
    vol = df['Vol'].sum()
    oi = df.tail(1)['OI'].values[0]
    SQL = "INSERT INTO FUTURE_DAY_DATA VALUES ('{0}','{1}',{2},{3},{4},{5},{6},{7})".format \
        (today, code, High, Low, Open, Close, vol, oi)
    cur = Trading_CONN.cursor()
    cur.execute(SQL)
    cur.close()
    Trading_CONN.commit()

def update_today_data(info):
    code = info[0]
    days = info[1]
    is_call = info[2]
    multi = info[3]
    month = info[4]

    if not check_today_update(code):
        return
    SQL ="SELECT * FROM MIN_DATA WHERE SecurityID='{0}' AND date(DTime)='{1}'".format(code, today)
    df = pd.read_sql(SQL, Trading_CONN)
    df = df.drop(0) # 9:25 收到的是前一日的结算价
    Open = df.head(1)['sOpen'].values[0]
    Close = df.tail(1)['sClose'].values[0]
    High = df['sHigh'].max()
    Low = df['sLow'].min()
    vol = df['Vol'].sum()
    vol = -1
    SQL = "INSERT INTO DAY_DATA VALUES ('{0}','{1}',{2},{3},{4},{5},{6},{7},{8},{9},{10})".format\
        (today, code, High, Low, Open, Close, vol, days, is_call, multi, month)
    cur = Trading_CONN.cursor()
    cur.execute(SQL)
    cur.close()
    Trading_CONN.commit()
    return df

if __name__ == "__main__":
    opt_inst = get_today_inst()
    future_inst = get_today_future_inst()
    #y = get_today_data(x.values[0][0])
    for inst in opt_inst.values:
        update_today_data(inst)
    for inst in future_inst.values:
        update_today_future_data(inst[0])