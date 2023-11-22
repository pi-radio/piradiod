import time
import numpy as np

from piradio.devices import SampleBufferIn, SampleBufferOut, Trigger

sbos = [ SampleBufferOut(i) for i in range(8) ]
sbis = [ SampleBufferIn(i) for i in range(8) ]

trigger = Trigger()

for sb in sbos:
    sb.one_shot(False)
    sb.array = np.zeros(sb.nsamples)
    
for sb in sbis:
    sb.one_shot(True)

def capture():
    trigger.trigger()
    time.sleep(0.01)

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

rx_enables = _RXEnables()
tx_enables = _TXEnables()

def capture_mode(mode):
    if mode == "CW":
        for i in range(8):
            sbos[i].one_shot(False)
            rx_enables[i] = True
            tx_enables[i] = True

        trigger()

        for i in range(8):
            tx_enables[i] = False
    elif mode == "SYNC":
        for i in range(8):
            sbos[i].one_shot(True)
            rx_enables[i] = True
            tx_enables[i] = True
        
        
# legacy stupidity
def txCW():
    capture_mode("CW")
    
def txSYNC():
    capture_mode("SYNC")
        
