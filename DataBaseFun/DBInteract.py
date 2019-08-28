from DataBaseFun.DataBase import *
import pandas as pd


def get_last_etf_min(last=10):
    SQL = "SELECT * FROM ETF_MIN_DATA order by DTime DESC LIMIT {0}".format(last)
    df = pd.read_sql(SQL, Trading_CONN)
    return df


def get_last_min(code, last=10):
    SQL = "SELECT * FROM MIN_DATA WHERE SecurityID='{0}' order by DTime DESC LIMIT {1}".format(code, last)
    df = pd.read_sql(SQL, Trading_CONN)
    return df


def get_my_pos(code, stra):
    SQL = "SELECT * FROM POS WHERE SecurityID='{0}' AND StrategyID='{1}'".format(code, stra)
    df = pd.read_sql(SQL, Trading_CONN)
    return df


def get_all_my_pos(stra):
    SQL = "SELECT * FROM POS WHERE StrategyID='{0}'".format(stra)
    df = pd.read_sql(SQL, Trading_CONN)
    return df

def get_inst_info(code):
    SQL = "SELECT * FROM INST WHERE SecurityID='{0}'".format(code)
    df = pd.read_sql(SQL, Trading_CONN)
    return df


def get_vix(last=10):
    SQL = "SELECT * FROM VIX ORDER BY DTime DESC LIMIT {0}".format(last)
    df = pd.read_sql(SQL, Trading_CONN)
    return df


def get_trading_code(level, is_call, this_month=True, drop_adj=False, use_current_val=True):
    # 用最新数据可能有风险 选择的期权可能在日内发生变化
    # use_current_val 为 True 则采用昨日收盘价作为选择依据
    # 范围异常时输出最远端 并提示
    # 只支持当月次月
    if use_current_val:
        SQL = "SELECT sClose FROM ETF_MIN_DATA order by DTime DESC LIMIT 1"
        SQL_INST = "SELECT securityid, strike, multiple, IsCall, Month FROM INST WHERE Month>= 0"
    df = pd.read_sql(SQL, Trading_CONN)
    last_etf_close = df.values[0][0]
    inst_df = pd.read_sql(SQL_INST, Trading_CONN)
    if drop_adj:
        inst_df = inst_df[inst_df['multiple'] == 10000]
    if is_call:
        inst_df = inst_df[inst_df['IsCall'] == 1]
    else:
        inst_df = inst_df[inst_df['IsCall'] == 0]
    if this_month:
        inst_df = inst_df[inst_df['Month'] == 0]
    else:
        inst_df = inst_df[inst_df['Month'] == 1]
    inst_df['distance'] = abs(inst_df['strike'] - last_etf_close)
    inst_df = inst_df.sort_values('distance')
    atm_price = inst_df['strike'].values[0]
    atm_code = inst_df['securityid'].values[0]
    if is_call:
        waiting_list = inst_df[inst_df['strike'] > atm_price]['securityid'].values.tolist()
    else:
        waiting_list = inst_df[inst_df['strike'] < atm_price]['securityid'].values.tolist()
    waiting_list.insert(0, atm_code)
    try:
        chosen = waiting_list[level]
    except:
        chosen = waiting_list[-1]
        print("warning : this code may not be what you want. Sending the best one in market")
    return chosen


if __name__ == "__main__":

    x = get_last_min('10001872', 100)
    y = get_my_pos('10001872', 7001)
    z = get_inst_info('10001872')