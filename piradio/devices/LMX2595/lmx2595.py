import time

from piradio.devices.spidev import SPIDev

from .config import LMXConfig
from piradio.command import command, cmdproperty, CommandObject
from piradio.util import Freq

class LMX2595Dev(CommandObject):
    def __init__(self, name, spidev, **kwargs):
        #super().__init__(bus_no, dev_no, speed=250000, mode=0)

        self.spidev = spidev
        
        self.reset()
        
        self.config = LMXConfig(self.name, **kwargs)
        self.active_regs = None
                
    def write_reg(self, r):
        if self.active_regs is None:
            self.active_regs = self.config.regs
            
        v = self.active_regs[r]
        
        self.spidev.xfer([ r, (v >> 8) & 0xFF, v & 0xFF ])

    @command
    def dump_regs(self):
        self.config.dump_regs()

    @command
    def display(self):
        self.config.display()

    @command
    def reset(self):
        # put the device into reset
        self.spidev.xfer([ 0, 0, 7 ])

        time.sleep(0.01)

        # put the device into reset
        self.spidev.xfer([ 0, 0, 4 ])
        
    @command
    def program(self):
        for rno in range(106, 0, -1):
            self.write_reg(rno)
            time.sleep(0.01)

        self.config.fcal_en = 0
        #v = self.active_regs[0] & ~8
        self.write_reg(0)

        time.sleep(0.01)
            
        self.config.fcal_en = 1
        #v = self.active_regs[0] | 8
        self.write_reg(0)

    @command
    def disable_output(self, output : str):
        if output == "A":
            self.config.Apd = True
        elif output == "B":
            self.config.Bpd = True
        else:
            raise RuntimeError("Invalid Output")
        
        self.write_reg(44)

    @command
    def enable_output(self, output : str):
        if output == "A":
            self.config.Apd = False
        elif output == "B":
            self.config.Bpd = False
        else:
            raise RuntimeError("Invalid Output")
        
        self.write_reg(44)

    @command
    def tune(self, A : Freq, B : Freq = None):
        self.config.tune(A, B)
    
        
    @cmdproperty
    def Apwr(self):
        return self.config.Apwr

    @Apwr.setter
    def Apwr(self, v : int):
        v = int(v)
        assert v >= 0 and v < 64
        self.disable_output("A")
        self.config.Apwr = v
        self.write_reg(44)
        self.enable_output("A")


    @cmdproperty
    def Bpwr(self):
        return self.config.Bpwr

    @Bpwr.setter
    def Bpwr(self, v : int):
        v = int(v)
        assert v >= 0 and v < 64
        self.disable_output("B")
        self.config.Apwr = v
        self.write_reg(45)
        self.enable_output("B")
