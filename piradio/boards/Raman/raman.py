import os
import sys
import time
import traceback
import glob
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
from pathlib import Path

from piradio.command import CommandObject, command, cmdproperty
from piradio.output import output
from piradio.devices import SysFS, SPIDev
from piradio.devices import Renesas_8T49N240, LMX2595Dev
from piradio.devices import AXI_GPIO
from piradio.devices import Trigger
from piradio.devices import LTC5594Dev
from piradio.util import MHz
from piradio import zcu111

sysfs_dt_path = Path("/sys/firmware/devicetree/base")
sysfs_devices_path = Path("/sys/devices/platform")

direct=True

class Raman(CommandObject):
    def __init__(self):
        output.info("Initializing C.V. Raman (a.k.a. SDRv2)...")

        # setup GPIOs

        self.find_gpio()
        
        l = glob.glob("/sys/firmware/devicetree/base/__symbols__/*pl_gpio")

        if len(l) == 0:
            print("Could not find FPGA PL.  Please ensure firmware is loaded")

        if len(l) != 1:
            raise RuntimeError(f"FPGA configuration invalid: GPIOs found: {l}")
        
        gpio = Path(l[0]).name

        if gpio == "pl_gpio":
            self.OFDM = False
            self._NCO_freq = MHz(1000)
        else:
            self.OFDM = True
            self._NCO_freq = MHz(737.2)
            
        
        self.children.gpio = AXI_GPIO(gpio)
        self.children.reset_gpio = self.gpio.outputs[0]

        self.reset_gpio.val = 0
        time.sleep(0.25)
        
        self.reset_gpio.val = 1
        time.sleep(0.25)
        
        self.children.clk_root = Renesas_8T49N240()
        self.children.lo_root = LMX2595Dev("LO Root", SPIDev(2, 24), f_src=MHz(45), A=self.LO_freq, B=self.LO_freq, Apwr=10, Bpwr=10)

        self.children.LTC5594 = [ LTC5594Dev(SPIDev(2, 6 * card + radio + 4)) for card in range(4) for radio in range(2) ]

        for ltc in self.LTC5594:
            ltc.lvcm = 2
            ltc.band = 0
            ltc.cf1 = 8
            ltc.lf1 = 1
            ltc.cf2 = 21
            ltc.ampg = 0
            ltc.program()

            
        
        
    def find_gpio(self):
        gpios = list(Path("/sys/bus/platform/devices").glob("[ab]*.gpio"))
        
    @command
    def init(self):
        self.reset()

        if direct:
            from piradio.devices.sivers import Eder, EderChipNotFoundError

            self.radios = [ None ] * 8
            
            for card in range(4):
                for radio in range(2):
                    n =  2*card + radio

                    if self.radios[n] is not None:
                        # check to make usre it's still there
                        continue
                
                    try:
                        eder = Eder(SPIDev(2, 6 * card + 2 * radio + 1, mode=0), n)
                        self.radios[n] = eder
                        eder.INIT()
                        eder.freq = 60e9
                    except EderChipNotFoundError:
                        print(f"WARNING: Radio {n} not found")
                        pass
                    except Exception as e:
                        print(f"Failed to detect radio {2 * card + radio}")
                        traceback.print_exc()
        
        
    @command
    def reset(self):
        self.reset_gpio.val = 0
        time.sleep(0.25)
        self.reset_gpio.val = 1
        time.sleep(0.25)

        output.info("Programming clock tree and LO...")
        

        self.clk_root.program()

        if not self.OFDM:
            if self.NCO_freq == MHz(1000):
                os.system(f"rfdcnco fs/4")
            else:
                os.system(f"rfdcnco set {self.NCO_freq.Hz}")

        self.lo_root.program()


    @cmdproperty
    def LO_freq(self):
        if self.OFDM:
            return MHz(737.2)

        return self.NCO_freq
                
    @cmdproperty
    def NCO_freq(self):
        return self._NCO_freq

    @NCO_freq.setter
    def NCO_freq(self, v):
        print(f"Changing NCO freq to {v}")
        self._NCO_freq = v
        self.children.lo_root.tune(self._NCO_freq, self._NCO_freq)
        self.children.lo_root.program()

        os.system(f"rfdcnco {self._NCO_freq.Hz}")

