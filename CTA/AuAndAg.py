from DataBaseFun.DataBase import Trading_CONN
import pandas as pd
import matplotlib.pyplot as plt

SQL_AU = "select distinct DTime, sClose from FUTURE_DAY_DATA where SecurityID like 'au%' order by  DTime desc"

x = pd.read_sql(SQL_AU, Trading_CONN, index_col='DTime')
x.plot()
plt.show()