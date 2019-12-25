import pandas as pd
import numpy as np
from ToolBox.DataBaseFun.DataBase import *
import datetime
# 引入分钟线


def realized_vol(date_n):
    SQL = "SELECT sClose FROM ETF_MIN_DATA where date(DTime)='{0}'".format(date_n)
    df = pd.read_sql(SQL, Trading_CONN)
    rv = np.sqrt((df.pct_change()**2).sum() * 252)
    return rv.iloc[0] * 100


def _cal_ivol(df_nm, expire_date):
    NT = expire_date * 240
    T = NT / (365 * 240)
    R = 0.04
    S_info = df_nm.loc[df_nm.price_diff == df_nm.price_diff.min()].iloc[0]
    F = S_info.strike + np.exp(R * T) * (S_info.call_price - S_info.put_price)
    if df_nm.iloc[0].strike > F:
        K0 = df_nm.iloc[0].strike
    else:
        K0 = df_nm[df_nm.strike <= F].iloc[-1].strike
    strikei1 = df_nm.strike.shift(-1)
    strikei1 = strikei1.fillna(strikei1.iloc[-2] + 0.05 if strikei1.iloc[-2] < 3 else strikei1.iloc[-2] + 0.1)
    strikei2 = df_nm.strike.shift(1)
    strikei2 = strikei2.fillna(strikei2.iloc[1] - 0.05 if strikei2.iloc[1] <= 3 else strikei2.iloc[1] - 0.1)
    dKi = (strikei1-strikei2) / 2
    Ki = df_nm.strike
    Pki = df_nm.apply(lambda row: row.put_price if row.strike < K0 else(row.call_price if row.strike > K0
                                                                       else (row.call_price+row.put_price) / 2), axis=1)
    ivol = np.sqrt((sum(Pki*dKi/(Ki**2)*np.exp(R*T))*2/T-1/T*((F/K0-1)**2)))
    return(ivol)


def cal_ivix(date_n):
    sql = """
    select * from (select * from DAY_DATA where date(DTime)='{0}') t1
    inner join (select SecurityID as s1, Strike from INST )  t2
    on t1.SecurityID=t2.s1 order by t1.ExpiryDays,Strike
            """.format(date_n)
    data1 = pd.read_sql(sql, Trading_CONN)
    call_opt = data1[data1.IsCall == 1].reset_index()
    put_opt = data1[data1.IsCall == 0].reset_index()
    df1 = pd.DataFrame()
    df1['strike'] = call_opt['Strike']
    df1['call_code'] = call_opt['SecurityID']
    df1['expiredate']= call_opt['ExpiryDays']
    df1['put_code'] = put_opt['SecurityID']
    df1['call_price'] = call_opt["sClose"]
    df1['put_price'] = put_opt["sClose"]
    df1['price_diff'] = (df1.call_price-df1.put_price).abs()
    month_list = df1.expiredate.drop_duplicates()
    i_m = 0
    expdate_n = month_list.iloc[i_m]
    T1 = expdate_n*240/(365*240)
    df_nm = df1[df1.expiredate == expdate_n].copy()
    expdate_nn = month_list.iloc[i_m+1]
    T2 = expdate_nn*240/(365*240)
    df_nnm = df1[df1.expiredate == expdate_nn].copy()
    vol_1 = _cal_ivol(df_nm, expdate_n)
    vol_2 = _cal_ivol(df_nnm, expdate_nn)
    if month_list.iloc[i_m] > 30:
        ivix = vol_1*100
    else:
        ivix = 100*np.sqrt((T1*vol_1**2*(expdate_nn-30)/(expdate_nn-expdate_n)+T2*vol_2**2*(30-expdate_n)/(expdate_nn-expdate_n))*365/30)
    return ivix


def check_and_update(now):
    vix = cal_ivix(now)
    rv = realized_vol(now)
    SQL_check = "SELECT * FROM VIX WHERE DTime='{0}'".format(now)
    df = pd.read_sql(SQL_check, Trading_CONN)
    if df.empty:
        SQL = "INSERT INTO VIX VALUES ('{0}',{1},{2})".format(now, vix, rv)
        cur = Trading_CONN.cursor()
        cur.execute(SQL)
        Trading_CONN.commit()


if __name__ == '__main__':
    now = str(datetime.datetime.now())[:10]
    check_and_update(now)