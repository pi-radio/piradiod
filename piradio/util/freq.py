import math
import functools
from json import JSONEncoder, JSONDecoder
from collections import OrderedDict

import numpy as np



@functools.total_ordering
class Freq:
    freq_exp = OrderedDict([
        ('GHz', 9),
        ('MHz', 6),
        ('KHz', 3),
        ('Hz', 0),
        ('mHz', -3),
        ('uHz', -6)
    ])
    
    freq_mult = OrderedDict([ (s,10**v) for s,v in freq_exp.items() ])
    
    def __init__(self, f, unit='Hz'):
        if isinstance(f, Freq):
            self.hz = f.hz
            return
        
        self.hz = f * self.freq_mult[unit]
        
    def v(self, unit):
        return self.hz / self.freq_mult[unit]

    @property
    def friendly_tuple(self):
        for s, v in self.freq_mult.items():
            if np.abs(self.hz) >= v:
                return (v, s)
            
        return (1, "Hz")
        
    
    @property
    def GHz(self):
        return self.v('GHz')

    @property
    def MHz(self):
        return self.v('MHz')
    
    @property
    def KHz(self):
        return self.v('KHz')

    @property
    def Hz(self):
        return self.hz

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
        

    def __add__(self, other):
        return Freq(self.hz + other.hz)

    def __sub__(self, other):
        return Freq(self.hz - other.hz)
    
    def __mul__(self, other):
        assert not isinstance(other, Freq)
        
        return Freq(self.hz * other)

    def __rmul__(self, other):
        assert not isinstance(other, Freq)
        
        return Freq(self.hz * other)

    
    def __truediv__(self, other):
        if isinstance(other, Freq):
            return self.hz/other.hz
        else:
            return Freq(self.hz/other)

    def __round__(self, rounding):
        return Freq(round(self.hz, int(math.log10(rounding.hz))))

    def __neg__(self):
        return Freq(-self.hz)
    
def GHz(x):
    return Freq(x * 1e9)

def MHz(x):
    return Freq(x * 1e6)

def KHz(x):
    return Freq(x * 1e3)

def Hz(x):
    return Freq(x)
 
