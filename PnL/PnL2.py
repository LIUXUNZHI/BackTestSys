import pandas as pd
from DataBaseFun.DataBase import *

## todo 期权的收益拆解

from PnL.PNLMgr import *
pnlMgr = PNLMgr()
SQL = "select * from TRADE where date(TradeTime)='2019-09-02'"
df = pd.read_sql(SQL, Trading_CONN)
for i in range(len(df)):
    this_trade = df.iloc[i]
    pnlMgr.insert_pos(this_trade['SecurityID'], this_trade['Price'], abs(this_trade['Vol']), this_trade['IsOpen'],
                          this_trade['IsLong'])