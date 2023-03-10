import time

from piradio.devices.spidev import SPIDev
from piradio.output import output
from piradio.command import command, CommandObject

from piradio.devices import AXI_GPIO




class HMC630x(CommandObject):
    def __init__(self, spi, csn):
        #super().__init__(bus_no, dev_no)
        self.ctrl = spi
        
        self.csn = csn;

        self.csn.dir = "out"
        self.csn.val = 1
        
    def xfer(self, v):
        print(v)
        return v
        
    @command
    def write_reg(self, reg : int, v : int):
        reg = int(reg)
        v = int(v)

        self.ctrl.begin()
        
        self.csn.val = 0

        for i in range(8):
            self.ctrl.shift(v&1)
            v>>=1

        for i in range(6):
            self.ctrl.shift(reg & 1)
            reg >>= 1

        self.ctrl.shift(1)

        c = self.chip_addr

        for i in range(3):
            self.ctrl.shift(c & 1)
            c >>= 1

        self.csn.val = 1
        self.ctrl.mosi_gpio.val = 0
        time.sleep(0.0001)

        #sent, received = self.ctrl.end()
        
    @command
    def read_reg(self, reg : int):
        reg = int(reg)

        self.ctrl.begin()
        
        self.csn.val = 0

        vin = 0
        v = 0
        
        for i in range(8):
            self.ctrl.shift(0)

        for i in range(6):
            self.ctrl.shift(reg & 1)
            reg >>= 1

        self.ctrl.shift(0)

        c = self.chip_addr

        for i in range(3):
            self.ctrl.shift(c & 1)
            c >>= 1

        self.csn.val = 1
        time.sleep(0.001)
        
        self.ctrl.shift(0)

        self.csn.val = 0
        time.sleep(0.001)

        retval = 0
        
        for bit in range(8):
            retval |= self.ctrl.shift(0) << bit
        
        self.csn.val = 1
        time.sleep(0.1)

        sent, received = self.ctrl.end()

        #print(f"{sent}=>{received} {retval:02x}")

        return retval
