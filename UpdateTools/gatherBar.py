# 这个文件夹中,每个文件都应该能单独执行
import pandas as pd
import datetime
from DataBaseFun.DataBase import *

today = datetime.datetime.today()
today = str(today)[:10]
#today = '2019-07-17'

def get_today_inst():
    SQL = "SELECT SecurityID, ExpiryDays, IsCall, Multiple, Month FROM INST WHERE Month>=0"
    df = pd.read_sql(SQL, Trading_CONN)
    return df


def check_today_update(id):
    SQL = "SELECT * FROM DAY_DATA WHERE SecurityID = '{0}' AND DTime='{1}'".format(id, today)
    df = pd.read_sql(SQL, Trading_CONN)
    return df.empty


def update_today_data(info):
    id = info[0]
    days = info[1]
    is_call = info[2]
    multi = info[3]
    month = info[4]

    if not check_today_update(id):
        return
    SQL ="SELECT * FROM MIN_DATA WHERE SecurityID='{0}' AND date(DTime)='{1}'".format(id, today)
    df = pd.read_sql(SQL, Trading_CONN)
    df = df.drop(0) # 9:25 收到的是前一日的结算价
    Open = df.head(1)['sOpen'].values[0]
    Close = df.tail(1)['sClose'].values[0]
    High = df['sHigh'].max()
    Low = df['sLow'].min()
    vol = df['Vol'].sum()
    vol = -1
    SQL = "INSERT INTO DAY_DATA VALUES ('{0}','{1}',{2},{3},{4},{5},{6},{7},{8},{9},{10})".format\
        (today, id, High, Low, Open, Close, vol, days, is_call, multi, month)
    cur = Trading_CONN.cursor()
    cur.execute(SQL)
    cur.close()
    Trading_CONN.commit()
    return df

if __name__ == "__main__":
    x = get_today_inst()
    #y = get_today_data(x.values[0][0])
    for info in x.values:
        update_today_data(info)