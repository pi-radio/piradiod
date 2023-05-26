import time

from piradio.devices.spidev import SPIDev
from piradio.output import output
from piradio.command import command, CommandObject

from piradio.devices import AXI_GPIO




class HMC630x(CommandObject):
    def __init__(self, spidev):
        #super().__init__(bus_no, dev_no)
        self.spidev = spidev
 
        
    def prolog(self, reg, v, rw):
        self.spidev.begin()
        
        for i in range(8):
            self.spidev.shift(v&1)
            v >>= 1

        for i in range(6):
            self.spidev.shift(reg & 1)
            reg >>= 1

        self.spidev.shift(rw)

        c = self.chip_addr

        for i in range(3):
            self.spidev.shift(c & 1)
            c >>= 1
        
    @command
    def write_reg(self, reg : int, v : int):
        reg = int(reg)
        v = int(v)

        self.prolog(reg, v, 1)

        self.spidev.end()
        
    @command
    def read_reg(self, reg : int):
        reg = int(reg)

        self.prolog(reg, 0, 0)

        self.spidev.dead_cycle()
        
        retval = 0
        
        for bit in range(8):
            retval |= self.spidev.shift(0) << bit

        self.spidev.end()

        return retval
