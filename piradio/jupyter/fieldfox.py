import sys
import pyvisa
import fieldfox
import h5py

import numpy as np
import matplotlib.pyplot as plt

from piradio.util import *
from piradio.util.spectrum import SpectrumFrom_dB_Power

rm = pyvisa.ResourceManager("@py")


_ff = None

class FFWrapper:
    def __getattr__(self, k):
        return getattr(_ff, k)

    def __setattr__(self, k, v):
        return setattr(_ff, k, v)

ff = FFWrapper()

def connect_ff(addr="10.77.6.2"):
    global _ff
    _ff = fieldfox.FieldFox(rm, addr)


def center_carrier():
    ff.sense.freq.center = 650e6
    ff.sense.freq.span = 10e6

    ff.trigger()
    ff.wait_long()

    ff.write("CALC:MARK1:FUNC:MAX")
    
    f = MHz(float(ff.query("CALC:MARK1:X"))/1e6)
    p = float(ff.query("CALC:MARK1:Y"))

    ff.sense.freq.center = f.hz

    ff.trigger()
    ff.wait_long()
    
    return f, p

def carrier_power():
    ff.trigger()
    ff.wait_long()
    return float(ff.query("CALC:MARKER1:Y"))

class Mod(sys.__class__):
    @property
    def ff(self):
        return _ff

#sys.modules[__name__].__class__ = Mod

#
# Duck type to jupyter.spectrum
#
class FFSpectrum(SpectrumFrom_dB_Power):

    def SINAD(self, f):
        p = self.linear_power[self.find_signal(f)]
        s = np.sum(self.linear_power) - p - self.LO_power_lin
        return 10 * np.log10(p / s)

    def SFDR(self, f):
        b = self.find_signal(f)
        
        a1 = np.max(self.power[:b])
        a2 = np.max(self.power[b+1:])
        
        return self.power[b] - max(a1, a2)
        
    @classmethod
    def capture(cls, f_offset = Freq(0), p_offset = None):
        ff.trigger()
        ff.wait_long()
        
        c = ff.trace_data()

        freq = np.array([Freq(f) + f_offset for f in c[:, 0] ])
            
        power = c[:,1]

        if p_offset is not None:
            power = power + p_offset
        
        return FFSpectrum(freq, power)
