import math
import functools
from json import JSONEncoder, JSONDecoder
from collections import OrderedDict

import numpy as np

# 1 Watt at Z0 is sqrt(R) V
def _Vref(self, Z0):
    return np.sqrt(Z0)


# V == sqrt(P * R)
# log V = 1/2 (log P + log R)
# V == 1 -> log(V) == 0
#
# 0 = 1/2(log P + log R)


class Power:
    def __init__(self, W, Z0=50):
        self._W = W
        self._Z0 = Z0

    @property
    def W(self):
        return self._W
        
    @property
    def dBW(self):
        return 10 * np.log10(self._W)
        
    @property
    def dBm(self):
        return self.dBW + 30

    @property
    def dBV(self):
        # 1V reference is where log P == -log R
        return self.dBW + 10 * np.log10(self._Z0)

    @property
    def dBmV(self):
        # power drops by 20 dB for every 10dB of V because of the square
        return self.dBV + 60

    def __str__(self):
        return f"{self.dBm:.2f} dBm"
    
    def __repr__(self):
        return f"<|{self.dBm} dBm|>"

def dBW(v, Z0=50):
    return Power(10**(v/10), Z0)

def dBm(v, Z0=50):
    return dBW(v-30, Z0)

def dBV(v, Z0=50):
    return dBW(v - 10 * np.log10(Z0), Z0)

def dBmV(v, Z0=50):
    return dBV(v - 60, Z0)
