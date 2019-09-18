from StraMgr.StraMgr2 import StrategyBase
from DataBaseFun.DBInteract import *
from Strategys.Order import *
from OptionTool.OptionMgr import *
import datetime


class VixStra(StrategyBase):

    def __init__(self, strategy_id, base_vol, notional):
        self._leveage = 1.5
        self._order_id = 0
        self._notional = notional
        self.base_vol = base_vol
        self._do_open = False
        self._do_close = False
        self._start_ETF_pirce = None
        self._is_stoped = False
        self._call_code = get_opt_trading_code(1, 1)
        self._put_code = get_opt_trading_code(1, 0)
        super().__init__(strategy_id)

    def _is_open_hour(self):
        hour = datetime.datetime.now().time().hour
        min = datetime.datetime.now().time().minute
        t = hour * 10000 + min * 100
        if 93000 < t < 143000:
            return True
        else:
            return False

    def _is_close_hour(self):
        hour = datetime.datetime.now().time().hour
        min = datetime.datetime.now().time().minute
        t = hour * 10000 + min * 100
        if 145000 < t < 145300:
            return True
        else:
            return False

    def _calc_signal(self):
        today_open = get_last_etf_min(1)
        vix_rv = get_vix(2)
        rv_diff = vix_rv['RV'][0] - vix_rv['RV'][1]
        ri_diff = vix_rv['VIX'][0] - vix_rv['RV'][0]
        vol_dir = 0
        if rv_diff > 1:
            vol_dir += 1
        elif rv_diff < -1:
            vol_dir -= 1

        if ri_diff >= 4:
            vol_dir -= 2
        elif ri_diff < 0:
            vol_dir += 2

        return vol_dir

    def close_all(self):
        print("ON MARKET CLOSE")
        print("CLOSE ALL")
        """
        holdings = get_all_my_opt_pos(self._stra_id)
        for i in range(len(holdings)):
            all_filled = holdings['FilledShort'][i] + holdings['FilledLong'][i]
            send_order(holdings['SecurityID'][i], BEST_PRICE, -all_filled,
                       False, self._order_id, self._stra_id, method="TWAP", batch=5, interval=10)
            self._order_id += 1
        """
        self._do_close = True

    def _check_and_stop_loss(self):

        now_pirce = get_last_etf_min(1)['sClose'][0]
        pct_chage = (now_pirce - self._start_ETF_pirce) / self._start_ETF_pirce
        holdings = get_all_my_opt_pos(self._stra_id)

        if abs(pct_chage) > get_vix(1)['VIX'][0] / 1600:   # gamma 止损
            print("STOP LOSS")
            print("CLOSE ALL")
            '''
             for i in range(len(holdings)):
                all_filled = holdings['FilledShort'][i] + holdings['FilledLong'][i]
                send_order(holdings['SecurityID'][i], BEST_PRICE, -all_filled,
                           False, self._order_id, self._stra_id, method="TWAP", batch=5, interval=10)
                self._order_id += 1
            '''
            self._is_stoped = True

    def run(self):
        if self._is_open_hour() and not self._do_open:
            vol_dir = self._calc_signal()
            self._start_ETF_pirce = get_last_etf_min(1)['sClose'][0]
            trade_vol = self._notional / 10000 / self._start_ETF_pirce * self._leveage
            if vol_dir > 0:
                print("LONG VOL")
                print('CODE: ' + self._call_code + ' VOL: ' + str(trade_vol))
                print('CODE: ' + self._put_code + ' VOL: ' + str(trade_vol))

                '''
                send_order(self._call_code, BEST_PRICE, self.base_vol,
                           True, self._order_id, self._stra_id, method="TWAP", batch=5, interval=10)
                self._order_id += 1
                send_order(self._put_code, BEST_PRICE, self.base_vol,
                           True, self._order_id, self._stra_id, method="TWAP", batch=5, interval=10)
                self._order_id += 1
                '''

            elif vol_dir < 0:
                print("SHORT VOL")
                print('CODE: ' + self._call_code + ' VOL: -' + str(trade_vol))
                print('CODE: ' + self._put_code + ' VOL: -' + str(trade_vol))
                '''
                send_order(self._call_code, BEST_PRICE, -self.base_vol,
                           True, self._order_id, self._stra_id, method="TWAP", batch=5, interval=10)
                self._order_id += 1
                send_order(self._put_code, BEST_PRICE, -self.base_vol,
                           True, self._order_id, self._stra_id, method="TWAP", batch=5, interval=10)
                self._order_id += 1
                '''
            self._do_open = True
        if not self._is_stoped and self._do_open:   # 止损后 日内不再交易
            self._check_and_stop_loss()
        if self._is_close_hour() and not self._do_close:
            self.close_all()
