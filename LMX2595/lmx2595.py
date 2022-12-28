import time

from spidev import SPIDev

from .config import LMXConfig
from picommand import picommand

class LMX2595Dev(SPIDev):
    def __init__(self, bus_no, dev_no):
        super().__init__(bus_no, dev_no)

        self.config = LMXConfig()
        self.active_regs = None
        
        # put the device into reset
        self.dev.transfer([ 0, 0, 2])

        time.sleep(0.01)

        v = self.config.regs[0]

        self.dev.transfer([ 0, v >> 8, v & 0xFF])

        
    def write_reg(self, r, v):
        self.dev.transfer([ r, (v >> 8) & 0xFF, v & 0xFF ])

    @picommand
    def display(self):
        self.config.display()
        
    @picommand
    def program(self):
        if not self.active_regs:
            self.active_regs = self.config.regs
            
            for rno in range(106, -1, -1):
                self.write_reg(rno, self.active_regs[rno])

            time.sleep(0.01)

            self.write_reg(0, self.active_regs[0] | 0x8)
        else:           
            r = self.config.regs
        
            for rno in range(106, -1, -1):
                v = self.active_regs[rno]

                if v != r[rno]:
                    self.write_reg(rno, v)

            self.active_regs = r

    @picommand
    def tune(self, f0, f1):
        self.config.tune((f0, f1))
        self.program()
