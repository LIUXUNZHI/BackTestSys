from OptionTool.OptionMgr import *
import pandas as pd
class PNLNode:
    def __init__(self, price, vol, is_open, is_long, tradetime, **kwargs):
        self.filled_price = price
        self.vol = vol
        self.is_open = is_open
        self.is_long = is_long
        self.trade_time = tradetime
        self.ETF = None
        self.strike = None
        self.expiry = None
        self.call = None
        if "ETF" in kwargs.keys():
            self.ETF = kwargs['ETF']
        if "strike" in kwargs.keys():
            self.strike = kwargs["strike"]
        if "expiry" in kwargs.keys():
            self.expiry = kwargs["expiry"]
        if "call" in kwargs.keys():
            self.call = kwargs['call']


class PNLMgrBase(object):  # 设计成一个基类 衍生出 期权和期货不同的处理模式
    def __init__(self):
        self.pos_map = {}
        self.raw_PNL = 0
        self.fee = 0
        self.multi = 1

    def _calc_fee(self, is_open, is_long, vol, price):
        raise NotImplemented

    def _trade(self, order1, order2):  #撮合

        if order1.is_long: # 2 平 1 多头
            if order2.vol > order1.vol:
                trade_vol = min(order2.vol, order1.vol)
                self.raw_PNL += order1.vol * (order2.filled_price - order1.filled_price) * self.multi
                order2.vol -= trade_vol
                order1.vol -= trade_vol
                return False, order2, order1
            else:
                trade_vol = min(order2.vol, order1.vol)
                self.raw_PNL += order2.vol * (order2.filled_price - order1.filled_price) * self.multi
                order2.vol -= trade_vol
                order1.vol -= trade_vol
                return True, order2, order1
        if not order1.is_long:  # 2 平 1 空头
            if order2.vol > order1.vol:
                trade_vol = min(order2.vol, order1.vol)
                self.raw_PNL -= order1.vol * (order2.filled_price - order1.filled_price) * self.multi
                order2.vol -= trade_vol
                order1.vol -= trade_vol
                return False, order2, order1
            else:
                trade_vol = min(order2.vol, order1.vol)
                self.raw_PNL -= order2.vol * (order2.filled_price - order1.filled_price) * self.multi
                order2.vol -= trade_vol
                order1.vol -= trade_vol
                return True, order2, order1

    def insert_pos(self, code, price, vol, is_open, is_long, trade_time, **kwags):    # 应当隔夜仓位
        self._calc_fee(is_open, is_long, vol, price)
        if "ETF" not in kwags.keys():
            order2 = PNLNode(price, vol, is_open, is_long, trade_time)
        else:
            order2 = PNLNode(price, vol, is_open, is_long, trade_time,
                             ETF=kwags['ETF'], strike=kwags['strike'], expiry=kwags['expiry'], call=kwags['call'])
        if code not in self.pos_map.keys() and is_open:
            self.pos_map[code] = [order2]
        elif code in self.pos_map.keys():
            node_list = self.pos_map[code]
            if is_open:
                self.pos_map[code].append(order2)
            else:
                finish_tag = False
                while not finish_tag:
                    try:
                        order1 = self.pos_map[code].pop(0)
                    except:
                        order1 = PNLNode(0, 0, 0, 0, '0')
                    finish_tag, order2, order1 = self._trade(order1, order2)
                    if finish_tag and order2.vol != 0:
                        self.pos_map[code].append(order2)
                    if finish_tag and order1.vol != 0:
                        self.pos_map[code].insert(0, order1)

        else:
            raise ValueError("invalid close trade. wrong pos")

    def show_holdings(self, close_price=None):

        df = pd.DataFrame(columns=['code', 'IsLong', 'Pos', 'AvgPrice', 'ClosePrice'])
        for code in self.pos_map.keys():
            holds = self.pos_map[code]
            if len(holds) > 0:
                df2 = None
                IsLong = holds[0].is_long
                pos = 0
                avg_pirce = 0
                for trade in holds:
                    pos += trade.vol
                    avg_pirce += trade.vol * trade.filled_price
                avg_pirce = avg_pirce / pos
                if isinstance(close_price, dict):
                    c_price = close_price[code]
                    df2 = pd.DataFrame(columns=['code', 'IsLong', 'Pos', 'AvgPrice', 'ClosePrice'],
                                      data=[[code, IsLong, pos, avg_pirce, c_price]])
                else:
                    df2 = pd.DataFrame(columns=['code', 'IsLong', 'Pos', 'AvgPrice', 'ClosePrice'],
                                      data=[[code, IsLong, pos, avg_pirce, None]])
                df = df.append(df2)
        return df


class OptPNLMgr(PNLMgrBase):

    def __init__(self, broker_fee_per_contract, multi):
        super().__init__()
        self.multi = multi
        self.broker_fee = broker_fee_per_contract
        self.delta = 0
        self.gamma = 0
        self.theta = 0
        self.vega = 0

    def _calc_fee(self, is_open, is_long, vol, price=0):
        tax = 1.6
        if is_open and not is_long:
            tax = 0
        self.fee += abs(vol) * (tax + self.broker_fee)

    def _trade(self, order1, order2):  # 撮合
        opt = OptionMgr(order1.ETF, order1.strike, 0.03, order1.expiry / 255,
                        order1.call, model='Implied', price=order1.filled_price)
        opt2 = OptionMgr(order2.ETF, order2.strike, 0.03, order2.expiry / 255,
                        order2.call, model='Implied', price=order2.filled_price)
        if order1.is_long:  # 2 平 1 多头
            if order2.vol > order1.vol:
                trade_vol = min(order2.vol, order1.vol)
                self.raw_PNL += order1.vol * (order2.filled_price - order1.filled_price) * self.multi
                self.delta += order1.vol * (order2.filled_price - order1.filled_price) * opt.delta * self.multi
                self.gamma += 0.5 * order1.vol * (order2.filled_price - order1.filled_price) ** 2 * opt.gamma * self.multi
                self.theta += order1.vol * (order2.trade_time - order1.trade_time).total_seconds() \
                              / (365 * 360 * 60) * opt.theta * self.multi
                self.vega += order1.vol * opt.vega * (opt2.sigma - opt.sigma) * self.multi
                order2.vol -= trade_vol
                order1.vol -= trade_vol
                return False, order2, order1
            else:
                trade_vol = min(order2.vol, order1.vol)
                self.raw_PNL += order2.vol * (order2.filled_price - order1.filled_price) * self.multi

                self.delta += order2.vol * (order2.filled_price - order1.filled_price) * opt.delta * self.multi
                self.gamma += 0.5 * order2.vol * (order2.filled_price - order1.filled_price) ** 2 * opt.gamma * self.multi
                self.theta += order2.vol * (order2.trade_time - order1.trade_time).total_seconds() \
                              / (365 * 360 * 60) * opt.theta * self.multi
                self.vega += order2.vol * opt.vega * (opt2.sigma - opt.sigma) * self.multi

                order2.vol -= trade_vol
                order1.vol -= trade_vol
                return True, order2, order1
        if not order1.is_long:  # 2 平 1 空头
            if order2.vol > order1.vol:
                trade_vol = min(order2.vol, order1.vol)
                self.raw_PNL -= order1.vol * (order2.filled_price - order1.filled_price) * self.multi

                self.delta -= order1.vol * (order2.filled_price - order1.filled_price) * opt.delta * self.multi
                self.gamma -= 0.5 * order1.vol * (order2.filled_price - order1.filled_price) ** 2 * opt.gamma * self.multi
                self.theta -= order1.vol * (order2.trade_time - order1.trade_time).total_seconds() \
                              / (365 * 360 * 60) * opt.theta * self.multi
                self.vega -= order1.vol * opt.vega * (opt2.sigma - opt.sigma) * self.multi

                order2.vol -= trade_vol
                order1.vol -= trade_vol
                return False, order2, order1
            else:
                trade_vol = min(order2.vol, order1.vol)
                self.raw_PNL -= order2.vol * (order2.filled_price - order1.filled_price) * self.multi

                self.delta -= order2.vol * (order2.filled_price - order1.filled_price) * opt.delta * self.multi
                self.gamma -= 0.5 * order2.vol * (order2.filled_price - order1.filled_price) ** 2 * opt.gamma * self.multi
                self.theta -= order2.vol * (order2.trade_time - order1.trade_time).total_seconds() \
                              / (365 * 360 * 60) * opt.theta * self.multi
                self.vega -= order2.vol * opt.vega * (opt2.sigma - opt.sigma) * self.multi

                order2.vol -= trade_vol
                order1.vol -= trade_vol
                return True, order2, order1

class StockPNLMgr(PNLMgrBase):

    def __init__(self, broker_fee_pct):
        super().__init__()
        self.broker_fee = broker_fee_pct

    def _calc_fee(self, is_open, is_long, vol, price):
        tax = 0.001
        if not is_long:
            self.fee += price * abs(vol) * (tax + self.broker_fee)


class FuturePNLMgr(PNLMgrBase):

    def __init__(self, broker_fee_per_hand, multi):
        super().__init__()
        self.broker_fee = broker_fee_per_hand
        self.multi = multi

    def _calc_fee(self, is_open, is_long, vol, price):
        tax = 1.6
        if is_open and not is_long:
            tax = 0
        self.fee += abs(vol) * (tax + self.broker_fee)


if __name__ == "__main__":
    import pandas as pd
    from DataBaseFun.DataBase import *
    from datetime import datetime
    today = str(datetime.today())[:10]
    posMgr = OptPNLMgr(1.6, 10000)
    SQL = "select * from TRADE where date(TradeTime)='2019-09-03'"
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
    SQL_INSERT = "INSERT INTO OptPNL VALUES ('{0}','{1}',{2},'{3}',{4},{5},{6},{7})".\
        format(today, "VIX", posMgr.raw_PNL - posMgr.fee, 'SHORT', posMgr.delta, posMgr.gamma, posMgr.theta, posMgr.vega)
    cur = Trading_CONN.cursor()
    cur.execute(SQL)
    Trading_CONN.commit()