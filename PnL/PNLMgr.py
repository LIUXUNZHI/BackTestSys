
class PNLNode:
    def __init__(self, price, vol, is_open, is_long, **kwargs):
        self.filled_price = price
        self.vol = vol
        self.is_open = is_open
        self.is_long = is_long
        self.ETF = None
        if "ETF" in kwargs.keys():
            self.ETF = kwargs['ETF']


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

    def insert_pos(self, code, price, vol, is_open, is_long):    # 应当隔夜仓位
        self._calc_fee(is_open, is_long, vol, price)
        order2 = PNLNode(price, vol, is_open, is_long)
        if code not in self.pos_map.keys() and is_open:
            pos_node = PNLNode(price, vol, is_open, is_long)
            self.pos_map[code] = [pos_node]
        elif code in self.pos_map.keys():
            node_list = self.pos_map[code]
            if is_open:
                pos_node = PNLNode(price, vol, is_open, is_long)
                self.pos_map[code].append(pos_node)
            else:
                finish_tag = False
                while not finish_tag:
                    try:
                        order1 = self.pos_map[code].pop(0)
                    except:
                        order1 = PNLNode(0, 0, 0, 0)
                    finish_tag, order2, order1 = self._trade(order1, order2)
                    if finish_tag and order2.vol != 0:
                        self.pos_map[code].append(order2)
                    if finish_tag and order1.vol != 0:
                        self.pos_map[code].insert(0, order1)

        else:
            raise ValueError("invalid close trade. wrong pos")
            #self.pos_map.update({code: node_list})


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
    posMgr = OptPNLMgr(1.6, 10000)
    SQL = "select * from TRADE where date(TradeTime)='2019-09-03'"
    df = pd.read_sql(SQL, Trading_CONN)
    for i in range(len(df)):
        this_trade = df.iloc[i]
        posMgr.insert_pos(this_trade['SecurityID'], this_trade['Price'], abs(this_trade['Vol']), this_trade['IsOpen'],
                          this_trade['IsLong'])
