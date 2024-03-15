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

    def __abs__(self):
        return Freq(abs(self.hz))

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

    def __rtruediv__(self, other):
        assert not isinstance(other, Time)

        if isinstance(other, Freq):
            return other.hz / self.hz
        else:
            return Time(other / self.hz)

    def __rfloordiv__(self, other):
        assert not isinstance(other, Time)

        if isinstance(other, Freq):
            return other.hz / self.hz
        else:
            return Time(other / self.hz)
        
        
    def __truediv__(self, other):
        if isinstance(other, Freq):
            return self.hz/other.hz
        else:
            return Freq(self.hz/other)

    def __floordiv__(self, other):
        if isinstance(other, Freq):
            return int(self.hz // other.hz)

        return Freq(self.hz//other)
        
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
 
def toGHz(x):
    return x.GHz

def toMHz(x):
    return x.MHz

def toKHz(x):
    return x.KHz

def toHz(x):
    return x.Hz


toGHz = np.vectorize(toGHz)
toMHz = np.vectorize(toMHz)
toKHz = np.vectorize(toKHz)
toHz = np.vectorize(toHz)

@functools.total_ordering
class Time:
    time_mult = OrderedDict([
        ('d', 24 * 60 * 60),
        ('h', 60 * 60),
        ('m', 60),
        ('s', 1),
        ('ms', 1e-3),
        ('us', 1e-6),
        ('ns', 1e-9)
    ])

    def __init__(self, s, unit='s'):
        if isinstance(s, Time):
            self.s = s.s
            return

        if isinstance(s, Freq):
            raise RuntimeError("Strange Freq->Time conversion")
        
        self.s = s * self.time_mult[unit]

    def v(self, unit):
        return self.hz / self.time_mult[unit]

    @property
    def friendly_tuple(self):
        for s, v in self.time_mult.items():
            if np.abs(self.s) >= v:
                return (v, s)
            
        return (1, "s")
        
    
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

        return format(self.s/v, spec) + s

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
            return Time(self.s/other)

    def __floordiv__(self, other):
        assert not isinstance(other, Freq)

        print(f"Floordiv {self} {other}")

        if isinstance(other, Time):
            return self.s//other.s
        else:
            return Time(self.s//other)

    def __rtruediv__(self, other):
        assert not isinstance(other, Freq)
        
        if isinstance(other, Time):
            return other.s/self.s
        else:
            return Freq(other/self.s)

    def __rfloordiv__(self, other):
        assert not isinstance(other, Freq)
        
        if isinstance(other, Time):
            return other.s//self.s
        else:
            return Freq(other//self.s)

        
    def __round__(self, rounding):
        return Time(round(self.s, int(math.log10(rounding.s))))

    def __neg__(self):
        return Time(-self.s)

