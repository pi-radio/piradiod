import sys
import pyvisa
import fieldfox
from piradio.util import *

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
