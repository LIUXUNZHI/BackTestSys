import pandas as pd
from ToolBox.DataBaseFun.DataBase import *
from ToolBox.PNL.PNLMgr import *
from datetime import datetime

today = str(datetime.today())[:10]
posMgr = OptPNLMgr(1.6, 10000)
SQL = "select * from TRADE where date(TradeTime)='{0}'".format(today)
df = pd.read_sql(SQL, Trading_CONN)
SQL2 = "SELECT * FROM INST"
df2 = pd.read_sql(SQL2, Trading_CONN)
for i in range(len(df)):
    this_trade = df.iloc[i]
    expiry = df2[df2['SecurityID'] == this_trade['SecurityID']]['ExpiryDays'].values[0]
    strike = df2[df2['SecurityID'] == this_trade['SecurityID']]['Strike'].values[0]
    call = 'C' if df2[df2['SecurityID'] == this_trade['SecurityID']]['IsCall'].values[0] == 1 else 'P'

    posMgr.insert_pos(this_trade['SecurityID'], this_trade['Price'], abs(this_trade['Vol']), this_trade['IsOpen'],
                      this_trade['IsLong'], this_trade['TradeTime'],
                      ETF=this_trade['ETF'], strike=strike, call=call, expiry=expiry)
    posMgr.show_holdings()
'''
SQL_INSERT = "INSERT INTO OptPNL VALUES ('{0}','{1}',{2},{3},{4},{5},{6},{7})". \
    format(today, "VIX", posMgr.raw_PNL - posMgr.fee,
           posMgr.delta, posMgr.gamma, posMgr.theta, posMgr.vega, posMgr.fee)
cur = Trading_CONN.cursor()
cur.execute(SQL_INSERT)
Trading_CONN.commit()
'''
