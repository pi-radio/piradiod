import os
import time

from piradio.command import CommandObject, command
from piradio.output import output
from piradio.devices import SPIDev
from piradio.devices import LMX2595Dev
from piradio.devices import MAX11300Dev

from .hcport import HCPort

class LNA(CommandObject):
    def __init__(self, dev):
        self.MAX11300 = dev

        self.VDD_target = 0.95
        self.VGG_target = 0.62

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
        output.print(f"LNA:")
        self.children.VDD.status("VDD: ")
        output.print(f"VGG: {1000.0*self.children.VGG.dac:4.0f} mV")
        
        
class Mixer(CommandObject):
    def __init__(self, dev):
        self.MAX11300 = dev

        self.VGG_target = 0.8

        self.children.VGG = HCPort(dev, (4, 5, 6), self.VGG_target)

    @command
    def up(self):
        self.children.VGG.ramp_to(self.VGG_target)
        
    @command
    def down(self):
        self.children.VGG.ramp_to(0)

    @command
    def status(self):
        output.print("Mixer:")
        self.children.VGG.status("VGG: ")

        
class BBAmp(CommandObject):
    def __init__(self, dev):
        self.MAX11300 = dev

        self.VDD_target = 0.95

        self.children.VDD_1 = dev.port[3]
        self.children.VDD_2 = dev.port[13]

        self.children.VDD_1.range = 6
        self.children.VDD_1.dac = 0.0

        self.children.VDD_1.funcid = dev.FUNCID_DAC_MONITOR

        self.children.VDD_2.range = 6
        self.children.VDD_2.dac = 0.0

        self.children.VDD_2.funcid = dev.FUNCID_DAC_MONITOR
        
    @command
    def up(self):
        self.children.VDD_1.ramp_to(self.VDD_target/2)
        self.children.VDD_2.ramp_to(self.VDD_target/2)
        self.children.VDD_1.ramp_to(self.VDD_target)
        self.children.VDD_2.ramp_to(self.VDD_target)

    @command
    def down(self):
        self.children.VDD_1.ramp_to(0)
        self.children.VDD_2.ramp_to(0)

    @command
    def status(self):
        output.print(f"VDD_1: {1000.0*self.children.VDD_1.dac:4.0f} mV")
        output.print(f"VDD_2: {1000.0*self.children.VDD_2.dac:4.0f} mV")
        

class X9(CommandObject):
    def __init__(self, dev):
        self.MAX11300 = dev

        self.VDD_target = 1.1
        self.VGG_target = 0.43

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
        self.children.VDD.status("VDD: ")
        output.print(f"VGG: {1000.0*self.children.VGG.dac:4.0f} mV")

        

class RXSide(CommandObject):
    def __init__(self, dev):
        self.MAX11300 = dev

        self.children.X9 = X9(dev)
        self.children.BB = BBAmp(dev)
        self.children.Mixer = Mixer(dev)
        self.children.LNA = LNA(dev)
        
    @command
    def up(self):
        self.children.X9.up()
        self.children.BB.up()
        self.children.Mixer.up()
        self.children.LNA.up()
        
    @command
    def down(self):
        self.children.X9.down()
        self.children.BB.down()
        self.children.Mixer.down()
        self.children.LNA.down()
        
    @command
    def status(self):
        self.children.X9.status()
        self.children.BB.status()
        self.children.Mixer.status()
        self.children.LNA.status()
        
class RX(CommandObject):
    def __init__(self):
        self.left_MAX11300 = MAX11300Dev(2, 8)
        self.right_MAX11300 = MAX11300Dev(2, 9) 

        self.left_MAX11300.setup()
        self.right_MAX11300.setup()
        
        self.children.L = RXSide(self.left_MAX11300)
        self.children.R = RXSide(self.right_MAX11300)

    @command
    def up(self):
        self.children.L.up()
        self.children.R.up()

    @command
    def status(self):
        output.print("RX Left side:")
        self.children.L.status()
        output.print("RX right side:")
        self.children.R.status()
