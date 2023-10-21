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
        
def txCW():    
    save_rx = [ rx_enables[i] for i in range(8) ]
    
    for i in range(8):
        sbos[i].one_shot(False)
        rx_enables[i] = False
        tx_enables[i] = True

    trigger.trigger()
        
    for i in range(8):
        rx_enables[i] = save_rx[i]
        tx_enables[i] = False
    
def txSYNC():
    for i in range(8):
        tx_enables[i] = True
        
