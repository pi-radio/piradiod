import os
import sys
import time
from pathlib import Path

from piradio.command import CommandObject, command
from piradio.output import output
from piradio.devices import SysFS, SPIDev
from piradio.devices import Renesas_8T49N240, LMX2595Dev
from piradio.devices import AXI_GPIO
from piradio.devices import SampleBufferIn, SampleBufferOut
from piradio.devices import Trigger
from piradio.devices.sivers import Eder

sysfs_dt_path = Path("/sys/firmware/devicetree/base")
sysfs_devices_path = Path("/sys/devices/platform")


class Raman(CommandObject):
    def __init__(self):
        print("Initializing C.V. Raman (a.k.a. SDRv2)...")

        # setup GPIOs

        self.children.gpio = AXI_GPIO("pl_gpio")

        self.children.reset = self.children.gpio[0]

        self.children.reset.dir = "out"
        self.children.reset.val = 0
        time.sleep(0.25)
        self.children.reset.val = 1
        time.sleep(0.25)
        
        self.children.clk_root = Renesas_8T49N240()

        self.children.clk_root.program()
        
        self.children.lo_root = LMX2595Dev("LO Root", 2, 24, f_src=45, A=1000, B=1000, Apwr=15, Bpwr=15)
        
        self.children.lo_root.program()
        
        self.children.input_samples = [ SampleBufferIn(i) for i in range(8) ]
        self.children.output_samples = [ SampleBufferOut(i) for i in range(8) ]

        self.children.trigger = Trigger()

        self.children.radios = [ Eder(SPIDev(2, 6 * card + 2 * radio + 1)) for card in range(1) for radio in range(2) ]
        
        
    @command
    def radar_test(self):
        self.children.radios[0].INIT()
        self.children.radios[1].INIT()

        self.children.radios[0].freq = 60e9
        self.children.radios[1].freq = 60e9
        
        self.children.radios[0].RX()

        self.children.radios[1].TX()

        self.children.output_samples[1].fill_sine(2e9/4096 * 16)

        #self.children.output_samples[1].plot()

        #self.children.trigger.trigger()
        
        self.children.output_samples[1].trigger()
        self.children.input_samples[0].trigger()

        self.children.input_samples[0].plot()

        #self.children.radios[1].SX()
