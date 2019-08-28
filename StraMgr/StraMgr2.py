import sys
#sys.path.append("../DataBaseFun")
#sys.path.append("../Strategys")
print(sys.path)
from DataBaseFun.DBInteract import *
from OptionTool.OptionMgr import *
from Strategys.vixStra import *
from Strategys.Order import *

import datetime
class StrategyBase:
    def __init__(self, strategy_id):
        self._stra_id = strategy_id

    def run(self):
        raise NotImplemented


class StraMgr(object):
    def __init__(self):
        self._stra_vector = []
        pass

    def add_strategy(self, strategy):
        #if isinstance(strategy, StrategyBase):
        self._stra_vector.append(strategy)

    def _is_trading_time(self):
        hour = datetime.datetime.now().time().hour
        min = datetime.datetime.now().time().minute
        t = hour * 10000 + min * 100
        if t > 93000 and t < 113000:
            return True
        elif t> 130000 and t < 145600:
            return True
        else:
            return False

    def run_all_strategy(self):
        for stra in self._stra_vector:
            if self._is_trading_time():
                stra.run()


class Stra01(StrategyBase):
    def __init__(self, strategy_id, signal, code):
        print('signal' + str(signal))
        self._signal = signal
        self._code = code
        super().__init__(strategy_id)

    def run(self):
        print("use stra01 signal")
        code = get_trading_code(0, 1)
        slow = get_last_min(code, 11)
        fast = get_last_min(code, 6)
        code_info = get_inst_info(code)
        etf = get_last_etf_min()
        last_etf = etf['sClose'].values[0]
        last_opt = fast['sClose'].values[0]
        opt = OptionMgr(last_etf, code_info['Strike'].iloc[0], 0.03, code_info['ExpiryDays'].iloc[0]/255,
                       "C" if code_info['IsCall'].iloc[0] == 1 else "P", model="Implied", price=last_opt)
        slow_ma = slow['sClose'].rolling(10).mean().dropna()
        fast_ma = fast['sClose'].rolling(5).mean().dropna()

        pos = get_my_pos(self._code, self._stra_id)
        print("LONG: ")
        print(pos['FilledLong'].iloc[0])
        print("SHORT: ")
        print(pos['FilledShort'].iloc[0])
        '''
        if fast_ma.iloc[-1] > slow_ma.iloc[-1] and fast_ma.iloc[-2] < slow_ma.iloc[-2]:
            print("UP CROSS: SEND LONG SIGNAL")
            send_order(self._code, BEST_PRICE, 10)
        elif fast_ma.iloc[-1] < slow_ma.iloc[-1] and fast_ma.iloc[-2] > slow_ma.iloc[-2]:
            print("DOWN CROSS: SEND SHORT SIGNAL")
            send_order(self._code, BEST_PRICE, -10)
        '''
        if fast_ma.iloc[-1] > fast_ma.iloc[-2]:
            print("UP CROSS: SEND LONG SIGNAL")
            print(code)
            #send_order(self._code, BEST_PRICE, 10, True)
        elif fast_ma.iloc[-1] < fast_ma.iloc[-2]:
            print("DOWN CROSS: SEND SHORT SIGNAL")
            print(code)
            #send_order(self._code, BEST_PRICE, -10, True)


class Stra02(StrategyBase):
    def __init__(self, strategy_id, signal):
        print('signal2' + str(signal))
        self._signal = signal
        super().__init__(strategy_id)

    def run(self):
        print("use stra02 signal")


if __name__ == "__main__":
    x = VixStra(703, 60)
    #x = Stra02(7002, 20)
    mgr = StraMgr()
    mgr.add_strategy(x)
    # mgr.add_strategy(y)
    from time import sleep
    while True:
        mgr.run_all_strategy()
        sleep(60)
