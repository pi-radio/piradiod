import os
import sys
import time
from pathlib import Path

from piradio.command import CommandObject, command
from piradio.output import output
from piradio.devices import SysFS, SPIDev, Renesas_8T49N240, LMX2595Dev, AXI_GPIO

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
        self.children.lo_root = LMX2595Dev(2, 24, f_src=45)

        
        
        
