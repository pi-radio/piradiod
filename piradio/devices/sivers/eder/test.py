from piradio.devices.sivers.eder.registers import generate_fake
from piradio.devices.sivers.eder.eder import Eder

class FakeSPI:
    def __init__(self):
        self.values = generate_fake()
        print(self.values[0:16])
        
    def xfer(self, x):
        addr = (x[0] << 5) | (x[1] >> 3)
        cmd = (x[1] & 0x7)

        d = x[2:]
        
        print(f"XFER: {addr} {cmd} {d}")

        retval = [ 0x00, 0x00 ] + self.values[addr:addr+len(d)]
        
        if cmd == 0:
            self.values[addr:addr+len(d)] = d
        elif cmd == 1:
            self.values[addr:addr+len(d)] &= ~d
        elif cmd == 2:
            self.values[addr:addr+len(d)] |= d
        elif cmd == 3:
            self.values[addr:addr+len(d)] ^= d
            
        
        return retval
        
e = Eder(FakeSPI())    

e.startup()
