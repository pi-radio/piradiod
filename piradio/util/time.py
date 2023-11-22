import math
import functools
from json import JSONEncoder, JSONDecoder
from collections import OrderedDict

import numpy as np

@functools.total_ordering
class Time:
    time_exp = OrderedDict([
        ('s', 0),
        ('ms', -3),
        ('us', -6),
        ('ns', -9)
    ])

    time_mult = OrderedDict([ (s,10**v) for s,v in time_exp.items() ])

    def __init__(self, s, unit='s'):
        if isinstance(f, Freq):
            self.s = f.s
            return
        
        self.s = s * self.freq_mult[unit]

    def v(self, unit):
        return self.hz / self.freq_mult[unit]

    @property
    def friendly_tuple(self):
        for s, v in self.freq_mult.items():
            if np.abs(self.hz) >= v:
                return (v, s)
            
        return (1, "Hz")
        
    
    @property
    def ms(self):
        return self.v('ms')

    @property
    def us(self):
        return self.v('us')
    
    @property
    def ns(self):
        return self.v('ns')

    def __str__(self):
        return self.__format__("")

    def __eq__(self, other):
        return self.hz == other.hz
            
    def __gt__(self, other):
        return self.hz > other.hz
            
    def __repr__(self):
        s = self.__format__("")
        return f"<{s}>"

    def __format__(self, spec):
        v, s = self.friendly_tuple

        return format(self.hz/v, spec) + s

    def __abs__(self):
        return Time(abs(self.s))

    def __add__(self, other):
        return Time(self.s + other.s)

    def __sub__(self, other):
        return Time(self.s - other.s)
    
    def __mul__(self, other):
        if isinstance(other, Freq):
            return self.s * other.hz

        if isinstance(other, Time):
            raise RuntimeError("Not doing s^2 yet...")
        
        return Freq(self.s * other)

    def __rmul__(self, other):
        if isinstance(other, Freq):
            return self.s * other.hz
            
        if isinstance(other, Time):
            raise RuntimeError("Not doing s^2 yet...")
        
        return Freq(self.s * other)
    
    def __truediv__(self, other):
        assert not isinstance(other, Freq)
        
        if isinstance(other, Time):
            return self.s/other.s
        else:
            return Freq(self.hz/other)

    def __floordiv__(self, other):
        print(f"Floordiv {self} {other}")
        if isinstance(other, Freq):
            return self.hz // other.hz

        return Freq(self.hz//other)
        
    def __round__(self, rounding):
        return Freq(round(self.hz, int(math.log10(rounding.hz))))

    def __neg__(self):
        return Freq(-self.hz)
