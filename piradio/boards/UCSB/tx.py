import os
import time
import atexit

from piradio.command import CommandObject, command
from piradio.output import output
from piradio.devices import SPIDev
from piradio.devices import LMX2595Dev
from piradio.devices import MAX11300Dev

from .hcport import HCPort

class CMOS_PA(CommandObject):
    def __init__(self, dev):
        self.MAX11300 = dev

        self.VDD_target = 0.80
        self.VGG_target = 0.55

        self.children.VGG = dev.port[15]
        
        self.children.VGG.funcid = dev.FUNCID_DAC_MONITOR
        self.children.VGG.range = 6
        self.children.VGG.dac = 0.0
        
        self.children.VDD = HCPort(dev, (10, 11, 12), self.VDD_target)

    @command
    def up(self):
        self.children.VDD.ramp_to(self.VDD_target/2)
        self.children.VGG.ramp_to(self.VGG_target/2)
        self.children.VDD.ramp_to(self.VDD_target)
        self.children.VGG.ramp_to(self.VGG_target)

    @command
    def down(self):
        self.children.VGG.ramp_to(0)
        self.children.VDD.ramp_to(0)

    @command
    def status(self):
        output.print(f"CMOS PA:")
        self.children.VDD.status(" VDD: ")
        output.print(f" VGG: {1000.0*self.children.VGG.dac:4.0f} mV")

class Mixer(CommandObject):
    def __init__(self, dev):
        self.MAX11300 = dev

        self.VLO_target = 0.8
        self.VCM_target = 0.55
        self.VDD_bias_target = 0.8
        
        self.children.VLO = HCPort(dev, (4, 5, 6), self.VLO_target)
        self.children.VCM = dev.port[3]
        self.children.VDD_bias = dev.port[13]

        self.children.VCM.funcid = dev.FUNCID_DAC_MONITOR
        self.children.VCM.range = 6
        self.children.VCM.dac = 0.0

        self.children.VDD_bias.funcid = dev.FUNCID_DAC_MONITOR
        self.children.VDD_bias.range = 6
        self.children.VDD_bias.dac = 0.0
        
    @command
    def up(self):
        self.children.VDD_bias.ramp_to(self.VDD_bias_target)
        self.children.VLO.ramp_to(self.VLO_target)
        self.children.VCM.ramp_to(self.VCM_target)
        
    @command
    def down(self):
        self.children.VLO.ramp_to(0)
        self.children.VCM.ramp_to(0)
        self.children.VDD_bias.ramp_to(0)

    @command
    def status(self):
        output.print("Mixer:")
        self.children.VGG.status(" VLO: ")
        output.print(f" VCM: {1000.0*self.children.VCM.dac:4.0f} mV")
        output.print(f" VDD_bias: {1000.0*self.children.VDD_bias.dac:4.0f} mV")
                

class X9(CommandObject):
    def __init__(self, dev):
        self.MAX11300 = dev

        self.VDD_target = 1.1
        self.VGG_target = 0.55

        self.children.VGG = dev.port[14]
        
        self.children.VGG.funcid = dev.FUNCID_DAC_MONITOR
        self.children.VGG.range = 6
        self.children.VGG.dac = 0.0
        
        self.children.VDD = HCPort(dev, (7, 8, 9), 1.1)


    @command
    def up(self):
        self.children.VDD.ramp_to(self.VDD_target/2)
        self.children.VGG.ramp_to(self.VGG_target/2)
        self.children.VDD.ramp_to(self.VDD_target)
        self.children.VGG.ramp_to(self.VGG_target)

    @command
    def down(self):
        self.children.VGG.ramp_to(0)
        self.children.VDD.ramp_to(0)

    @command
    def status(self):
        output.print("x9 MUltiplier:")
        self.children.VDD.status(" VDD: ")
        output.print(f" VGG: {1000.0*self.children.VGG.dac:4.0f} mV")

        
class InP_PA(CommandObject):
    def __init__(self, tx):
        self.tx = tx

        #
        # VCC Target 2.5V
        # Full scale 220mA ICC per die
        # 220 * 8 * 0.85 = ~1.5A
        #
        # Initial VCC = 2.2V @ 1.3A
        # Next VCC = 2.4V @ 1.5A
        # Then VCC = 2.5V @ 1.5A
        #
        # Derate VBB from 1.95 to 1.5
        
        self.scale = 0.8
        
        #self.VCC_target = 2.44 * self.scale
        #self.ICC_target = 1.39 * self.scale
        
        #self.VBB_target = 1.67 * self.scale
        #self.IBB_target = 0.062 * self.scale

        self.VCC_target = 2.2
        self.ICC_target = 1.3
        self.VBB_limit = 1.65
        self.IBB_limit = .07
        
        self.children.VCC = HCPort(self.tx.right_MAX11300, (0, 1, 2), self.VCC_target)
        self.children.VBB = HCPort(self.tx.left_MAX11300, (0, 1, 2), self.VBB_limit)

        self._is_up = False
        
    @property
    def is_up(self):
        return self._is_up

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
    
    @command
    def up(self):
        self.children.VCC.ramp_to(self.VCC_target/2)
        
        if self.ICC > 0.1:
            output.print("ICC with zero bias!")
            self.down()
            return

        self.children.VBB.ramp_to(self.VBB_limit/2)
        
        self.children.VCC.ramp_to(self.VCC_target)

        while self.children.VBB.V < self.VBB_limit and self.children.VCC.I < self.ICC_target:
            self.children.VBB.V += 0.025

        if (self.children.VCC.I - abs(self.ICC_target)) > 0.05:
            self.down()

        output.print("Final PA state:")
        self.status()
            
        self._is_up = True
            
    @command
    def down(self):
        output.print("InP down!")
        self.children.VBB.ramp_to(0.0)
        self.children.VCC.ramp_to(0.0)
        self._is_up = False

    @command
    def status(self):
        ICC = self.ICC
        IBB = self.IBB

        output.print(f"VCC: {self.children.VCC.V:3f} ICC: {ICC:3f} VBB: {self.children.VBB.V:3f} IBB: {IBB:3f}")        
        output.print(f"Per PA: ICC: {ICC/8:3f} IBB: {IBB/8:3f}")
        if IBB != 0:
            output.print(f"Composite β: {ICC/IBB:3f}")
        
    @command
    def watch(self):
        try:
            while True:
                output.print(f"ICC: {self.ICC} IBB: {self.IBB}")
                time.sleep(0.25)
        except KeyboardInterrupt:
            return
    
        
class TXSide(CommandObject):
    def __init__(self, tx, dev):
        self.tx = tx
        self.dev = dev

        self.children.X9 = X9(dev)
        self.children.Mixer = Mixer(dev)
        self.children.PA = CMOS_PA(dev)
        
    @command
    def up(self):
        if not self.tx.children.InP.is_up:
            output.error("Can not procceed -- power amp is not up")
            return

        self.children.X9.up()
        self.children.Mixer.up()
        self.children.PA.up()

    @command
    def down(self):
        self.children.PA.down()
        self.children.Mixer.down()
        self.children.X9.down()

    @command
    def status(self):
        self.children.PA.status()
        self.children.Mixer.status()
        self.children.X9.status()

        
class TX(CommandObject):
    def __init__(self):
        self.left_MAX11300 = MAX11300Dev(2, 10)
        self.right_MAX11300 = MAX11300Dev(2, 11) 

        self.left_MAX11300.setup()
        self.right_MAX11300.setup()

        self.children.InP = InP_PA(self)
        
        self.children.L = TXSide(self, self.left_MAX11300)
        self.children.R = TXSide(self, self.right_MAX11300)

        atexit.register(self.down)

    @command
    def down(self):
        self.children.L.down()
        self.children.R.down()
        self.children.InP.down()

    @command
    def up(self):
        self.children.InP.up()
        self.children.R.up()
        self.children.L.up()

    @command
    def status(self):
        output.print("TX Left side:")
        self.children.L.status()
        output.print("TX right side:")
        self.children.R.status()
        output.print("PA status:")
        self.children.InP.status()
