import time

from piradio.devices.spidev import SPIDev

from .config import LMXConfig
from piradio.command import command

class LMX2595Dev(SPIDev):
    def __init__(self, name, bus_no, dev_no, **kwargs):
        super().__init__(bus_no, dev_no, speed=250000, mode=0)

        self.reset()
        
        self.config = LMXConfig(self.name, **kwargs)
        self.active_regs = None
                
    def write_reg(self, r, v):
        self.dev.transfer([ r, (v >> 8) & 0xFF, v & 0xFF ])

    @command
    def dump_regs(self):
        self.config.dump_regs()

    @command
    def display(self):
        self.config.display()

    @command
    def reset(self):
        # put the device into reset
        self.dev.transfer([ 0, 0, 7 ])

        time.sleep(0.01)

        # put the device into reset
        self.dev.transfer([ 0, 0, 4 ])
        
    @command
    def program(self):
        self.active_regs = self.config.regs
        
        for rno in range(106, 0, -1):
            self.write_reg(rno, self.active_regs[rno])
            time.sleep(0.01)

        v = self.active_regs[0] & ~8
        self.write_reg(0, v)

        time.sleep(0.01)
            
        v = self.active_regs[0] | 8
        self.write_reg(0, self.active_regs[0] | 0x8)

