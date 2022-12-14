import os
import time
import atexit

from picommand import PiCommandObject, picommand
from pioutput import pioutput
from spidev import SPIDev
from LTC5584 import LTC5584Dev
from LMX2595 import LMX2595Dev
from MAX11300 import MAX11300Dev

from .hcport import HCPort

class CMOS_PA(PiCommandObject):
    def __init__(self, dev):
        self.MAX11300 = dev

        self.VDD_target = 1.1
        self.VGG_target = 0.62

        self.children.VGG = dev.port[15]
        
        self.children.VGG.funcid = dev.FUNCID_DAC_MONITOR
        self.children.VGG.range = 6
        self.children.VGG.dac = 0.0
        
        self.children.VDD = HCPort(dev, (10, 11, 12), self.VDD_target)

    @picommand
    def up(self):
        if not self.tx.inp.is_up:
            pioutput.error("Can not procceed -- power amp is not up")
            return

        self.children.VDD.ramp_to(self.VDD_target/2)
        self.children.VGG.ramp_to(self.VGG_target/2)
        self.children.VDD.ramp_to(self.VDD_target)
        self.children.VGG.ramp_to(self.VGG_target)

    @picommand
    def down(self):
        self.children.VGG.ramp_to(0)
        self.children.VDD.ramp_to(0)

    @picommand
    def status(self):
        pioutput.print(f"LNA:")
        self.children.VDD.status("VDD: ")
        pioutput.print(f"VGG: {1000.0*self.children.VGG.dac:4.0f} mV")

class InP_PA(PiCommandObject):
    def __init__(self, tx):
        self.tx = tx

        self.scale = 0.8
        
        self.VCC_target = 2.44 * self.scale
        self.ICC_target = 1.39 * self.scale
        
        self.VBB_target = 1.67 * self.scale
        self.IBB_target = 0.062 * self.scale

        self.children.VCC = HCPort(self.tx.right_MAX11300, (0, 1, 2), self.VCC_target)
        self.children.VBB = HCPort(self.tx.left_MAX11300, (0, 1, 2), self.VBB_target)

        
    @property
    def is_up(self):
        return False

    def oversample(self, p, N_bits=2):
        N_samp = 4 << N_bits
        epsilon = 2.5/2048/p.Rsense/N_bits

        v = p.I_oversample(N_samp)

        if abs(v) < epsilon:
            v = 0

        return v
        
    @property
    def ICC(self):
        return self.oversample(self.children.VCC)

    @property
    def IBB(self):
        return self.oversample(self.children.VBB)
    
    @picommand
    def up(self):
        self.children.VCC.ramp_to(self.VCC_target/2, display=True)

        ICC = self.ICC
        
        pioutput.print(f"ICC: {ICC}")

        if ICC > 0.1:
            self.down()
            return

        self.children.VBB.ramp_to(self.VBB_target/2)

        pioutput.print(f"ICC: {self.ICC}")

        ICC = self.ICC
        IBB = self.IBB

        if IBB != 0:
            ?? = ICC/IBB
            
            pioutput.print(f"ICC: {ICC} IBB: {IBB} Composite ??: {??}")
        else:
            pioutput.print(f"ICC: {ICC} IBB: {IBB}")
            
    @picommand
    def down(self):
        pioutput.print("InP down!")
        self.children.VBB.ramp_to(0.0)
        self.children.VCC.ramp_to(0.0)

    @picommand
    def watch(self):
        try:
            while True:
                pioutput.print(f"ICC: {self.ICC} IBB: {self.IBB}")
                time.sleep(0.25)
        except KeyboardInterrupt:
            return
    
        
class TXSide(PiCommandObject):
    def __init__(self, tx, dev):
        self.tx = tx
        self.dev = dev

    @picommand
    def up(self):
        if not self.tx.children.InP.is_up:
            pioutput.error("Can not procceed -- power amp is not up")
            return

    @picommand
    def down(self):
        pass
        
class TX(PiCommandObject):
    def __init__(self):
        self.left_MAX11300 = MAX11300Dev(2, 10)
        self.right_MAX11300 = MAX11300Dev(2, 11) 

        self.left_MAX11300.setup()
        self.right_MAX11300.setup()

        self.children.InP = InP_PA(self)
        
        self.children.L = TXSide(self, self.left_MAX11300)
        self.children.R = TXSide(self, self.right_MAX11300)

        atexit.register(self.down)

    @picommand
    def down(self):
        self.children.L.down()
        self.children.R.down()
        self.children.InP.down()
