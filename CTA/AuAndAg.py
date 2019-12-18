from DataBaseFun.DataBase import Trading_CONN
import pandas as pd
import matplotlib.pyplot as plt
import WindPy as win

USING_MY_DB = False

if USING_MY_DB:
    SQL_AU = "select distinct DTime, sClose from FUTURE_DAY_DATA where SecurityID like 'au1906' order by  DTime desc"
    SQL_AG = "select distinct DTime, sClose from FUTURE_DAY_DATA where SecurityID like 'ag1906' order by  DTime desc"
    x = pd.read_sql(SQL_AU, Trading_CONN, index_col='DTime')
    y = pd.read_sql(SQL_AG, Trading_CONN, index_col='DTime')
    y.plot()
    plt.show()
    x.plot()
    plt.show()
else:
    win.w.start()
    x = win.w.wsd("AU.SHF,AG.SHF", "close", "2019-05-19", "2019-09-17", "")
    data = pd.DataFrame(index=x.Times, data=x.Data )