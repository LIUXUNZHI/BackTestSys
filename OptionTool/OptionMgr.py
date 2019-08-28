import numpy as np
from scipy.stats import norm


class OptionMgr(object):
    def __init__(self, stock, strike, r, expire, call='C', model='Calc', **kwargs):
        self._stock = stock
        self._strike = strike
        self._r = r
        self._call = call
        self._expire = expire
        if model == 'Calc':
            sigma = kwargs['sigma']
            self._sigma = sigma
            self._d1 = None
            self._d2 = None
            self._discount = None
            self._p = self.price_option(self._sigma)
            self._delta = None
            self._gamma = None
            self._theta = None
            self._vega = None
            self.calculate_greeks()

        if model == "Implied":
            p = kwargs['price']
            self._p = p
            self._d1 = None
            self._d2 = None
            self._discount = None
            self._sigma = self.bisect_impvol()
            self.price_option(self._sigma)
            self._delta = None
            self._gamma = None
            self._theta = None
            self._vega = None
            self.calculate_greeks()


    def bisect_impvol(self):
        min_impvol = 0.001
        max_impvol = 1.5

        impvol_tick = 0.000001

        min_prc = self.price_option(min_impvol)
        max_prc = self.price_option(max_impvol)

        if min_prc <= self._p <= max_prc:

            while True:
                mid_impvol = (min_impvol + max_impvol) / 2
                if abs(max_impvol - min_impvol) <= impvol_tick:
                    break

                mid_prc = self.price_option(mid_impvol)

                if mid_prc > self._p:
                    max_impvol = mid_impvol
                else:
                    min_impvol = mid_impvol
        else:
            mid_impvol = None

        return mid_impvol

    def price_option(self, sigma):

        self._d1 = (np.log(self._stock / self._strike) + (self._r + sigma ** 2 / 2) * self._expire) / \
                   (sigma * np.sqrt(self._expire))
        self._d2 = self._d1 - sigma * np.sqrt(self._expire)
        self._discount = np.exp(-self._expire * self._r)
        N = norm(0, 1)
        if self._call == 'C':
            return self._stock * N.cdf(self._d1) - self._strike * self._discount * N.cdf(self._d2)
        elif self._call == 'P':
            return self._discount * self._strike * N.cdf(-self._d2) - self._stock * N.cdf(-self._d1)
        else:
            raise ValueError("Invaild Option Type Input.")

    def calculate_greeks(self):
        N = norm(0, 1)
        self._gamma = N.pdf(self._d1) / (self._stock * self._sigma * np.sqrt(self._expire))
        self._vega = self._stock * np.sqrt(self._expire) * N.pdf(self._d1)
        if self._call == 'C':
            self._delta = N.cdf(self._d1)
            self._theta = - self._stock * N.pdf(self._d1) * self._sigma / (2 * np.sqrt(self._expire)) - self._r * \
                            self._discount * self._strike * N.cdf(self._d2)
        elif self._call == 'P':
            self._delta = - N.cdf(-self._d1)
            self._theta = - self._stock * N.pdf(self._d1) * self._sigma / (2 * np.sqrt(self._expire)) + self._r * \
                            self._discount * self._strike * N.cdf(-self._d2)

    @property
    def p(self):
        return self._p

    @property
    def sigma(self):
        return self._sigma

    @property
    def delta(self):
        return self._delta

    @property
    def gamma(self):
        return self._gamma

    @property
    def theta(self):
        return self._theta

    @property
    def vega(self):
        return self._vega

if __name__ == '__main__':

    y = OptionMgr(2.963,2.95,0.03098,28/365,sigma=0.1866)
    # z = OptionMgr(2.9,2.9, 0.03, 2/365, model='Implied', price=0.0289)
    t = OptionMgr(844.32,805.72,0.03,10/365,sigma=0.42)
    # t.theta
    print(y.p,y.vega,y.theta,y.delta)

    print(t.theta,t.p,t.delta)
