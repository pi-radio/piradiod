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
from piradio.util import MHz

sysfs_dt_path = Path("/sys/firmware/devicetree/base")
sysfs_devices_path = Path("/sys/devices/platform")


class Monitor(CommandObject):
    def __init__(self):
        self.children.input_samples = [ SampleBufferIn(i) for i in range(8) ]
        self.children.output_samples = [ SampleBufferOut(i) for i in range(8) ]

        self.children.trigger = Trigger()

        self.children.input_samples[0].monitor()
