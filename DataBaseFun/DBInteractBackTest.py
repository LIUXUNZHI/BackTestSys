from DataBaseFun.DataBase import *
import pandas as pd


def get_opt_min_data(code, date):
    SQL = "SELECT * FROM MIN_DATA WHERE SecurityID='{0}' and day(DTime)={1}".format(code, date)
    df = pd.read_sql(SQL, Trading_CONN)
    return df


def get_etf_min_data(date):
    SQL = "SELECT * FROM ETF_MIN_DATA where day(DATE)={0}".format(date)
    df = pd.read_sql(SQL, Trading_CONN)
    return df


#todo
def get_opt_code(level, data, time=None):
    SQL1 = "SELECT * FROM "
    pass

