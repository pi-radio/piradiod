import sys
import time
from piradio.util import Freq, MHz, GHz, Samples

from .nrt import *

direct = False

board = None

if direct:
    from piradio.boards import SDRv2

    board = SDRv2()
    board.init()
else:    
    import Pyro5.api
    import Pyro5.errors

    class RadioProxy:
        def __init__(self, radio):
            self._radio = radio
            self.sbi = None
            self.sbo = None
        
        def __getattr__(self, k):
            return getattr(self._radio, k)

        def __setattr__(self, k, v):
            if k in [ "_radio", "sbi", "sbo" ]:
                self.__dict__[k] = v
                return
        
            try:
                return setattr(self._radio, k, v)
            except Exception as e:
                print("".join(Pyro5.errors.get_pyro_traceback()))
                raise e
        
    class BoardProxy:
        def __init__(self):
            self.server = Pyro5.api.Proxy("PYRO:eder_server@localhost:9999")
            self.radios = [ RadioProxy(self.server.get_radio(n)) for n in range(8) ]

    board = BoardProxy()


        
capture()
prcaptures = [ Samples(sbi) for sbi in sbis ]

for radio, sbi, sbo in zip(board.radios, sbis, sbos):
    if radio is None:
        continue

    radio.sbi = sbi
    radio.sbo = sbo
    

