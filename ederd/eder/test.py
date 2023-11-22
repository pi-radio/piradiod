import time

from piradio.command.shutdown import shutdown
from .registers import generate_fake
from .eder import Eder
from .tasks import shutdown

class FakeSPI:
    def __init__(self):
        self.values = generate_fake()
        print(self.values[0:16])
        
    def xfer(self, x):
        addr = (x[0] << 5) | (x[1] >> 3)
        cmd = (x[1] & 0x7)

        d = x[2:]

        if cmd != 4:
            d = d[:-1]
        
        retval = [ 0x00, 0x00 ] + self.values[addr:addr+len(d)]

        if cmd == 0:
            self.values[addr:addr+len(d)] = d
        elif cmd == 1:
            self.values[addr:addr+len(d)] = [ i & ~j for i, j in zip(self.values[addr:addr+len(d)], d) ] 
        elif cmd == 2:
            self.values[addr:addr+len(d)] = [ i | j for i, j in zip(self.values[addr:addr+len(d)], d) ] 
        elif cmd == 3:
            self.values[addr:addr+len(d)] = [ i ^ j for i, j in zip(self.values[addr:addr+len(d)], d) ] 

        if len(retval) < 16:
            print(f"XFER: {addr} {cmd} {d} | {retval[2:]} => {self.values[addr:addr+len(d)]}")
        else:
            print(f"XFER: {addr} {cmd} | LARGE                                      ")
            
        return retval
        
e = Eder(FakeSPI())    

e.INIT()

e.freq = 61e9

e.SX()

#e.startup()


time.sleep(20)

print("Shutting down")

shutdown.shutdown()

