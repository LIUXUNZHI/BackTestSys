from ToolBox.DataBaseFun.DBInteractBackTest import *
from ToolBox.PNL.PNLMgr import *

optPnL = OptPNLMgr(1.6, 10000)


class StrategyBase(object):
    def __init__(self, strategy_id):
        self._stra_id = strategy_id

    def run(self, date):
        raise NotImplemented

    def evaluate(self):
        raise NotImplemented


class Test(StrategyBase):
    def __init__(self, strategy_id):
        super.__init__(strategy_id)

    def run(self, date):
        call_code = get_opt_code(1, 1, 0, date)
        put_code = get_opt_code(1, 0, 0, date)




class BackTestEngine(object):

    def __init__(self, start_time, end_time, strategy=None, pnl=None):
        self._s_time = start_time
        self._e_time = end_time
        self._time_line = self._get_time_line()
        self._stra = strategy
        self._pnl_manager = pnl
        self.pnl = []
        if not isinstance(self._stra, StrategyBase):
            print("strategy init failed")
        if not isinstance(self._pnl_manager, OptPNLMgr):
            print("pnl init failed")

    def _get_time_line(self):
        return get_backtest_time_line(self._s_time, self._e_time)

    def run(self):
        for date in self._time_line:
            self._stra.run(str(date))
            self.pnl.append(self._pnl_manager.raw_PNL - self._pnl_manager.fee)





