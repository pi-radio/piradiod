import sys
import time
import numpy as np

from piradio.devices import SampleBufferIn, SampleBufferOut, Trigger

__sbos = None
__sbis = None

trigger = Trigger()

rx_enables = None
tx_enables = None

class _TXEnables:
    def __getitem__(self, n):
        return trigger.enables[n]
    
    def __setitem__(self, n, v):
        trigger.enables[n] = v

class _RXEnables:
    def __getitem__(self, n):
        return trigger.enables[n+8]
    
    def __setitem__(self, n, v):
        trigger.enables[n+8] = v

def nrt_setup(module):
    global __sbos, __sbis, rx_enables, tx_enables
    
    __sbis = module.sbis
    __sbos = module.sbos

    for sb in __sbos:
        sb.one_shot = False
        sb.array = np.zeros(sb.nsamples)
    
    for sb in __sbis:
        sb.one_shot = True

        rx_enables = _RXEnables()
        tx_enables = _TXEnables()

            
def capture():
    trigger.trigger()
    time.sleep(0.01)

def capture_mode(mode):
    if mode == "CW":
        for i in range(8):
            __sbos[i].one_shot = False
            rx_enables[i] = True
            tx_enables[i] = True
            
            trigger.trigger()

        for i in range(8):
            tx_enables[i] = False
    elif mode == "SYNC":
        for i in range(8):
            __sbos[i].one_shot = True
            rx_enables[i] = True
            tx_enables[i] = True        
