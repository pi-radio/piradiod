import os
import time
import atexit

from periphery import SPI
from periphery.spi import SPIError
from piradio.output import output
from piradio.command import CommandObject, command

class SPIDev(CommandObject):
    @property
    def device_file(self):
        return f"/dev/spidev{self.bus_no}.{self.dev_no}"
        
    @property
    def override_file(self):
        return f"/sys/bus/spi/devices/spi{self.bus_no}.{self.dev_no}/driver_override"
    
    def __init__(self, bus_no, dev_no, mode=0, speed=500000):
        output.debug(f"Attaching to device {bus_no}.{dev_no}");
        self.bus_no = bus_no
        self.dev_no = dev_no

        if not os.path.exists(self.device_file):
            with open(self.override_file, "w") as f:
                f.write("spidev\n")

            with open("/sys/bus/spi/drivers/spidev/bind", "w") as f:
                f.write(f"spi{self.bus_no}.{self.dev_no}")

            while not os.path.exists(self.device_file):
                time.sleep(0.1)

        self.dev = None
        i = 0
        
        while self.dev is None and i < 3:
            try:
                self.dev = SPI(self.device_file, mode, speed)
            except SPIError:
                i += 1

        if self.dev is None:
            raise RuntimeError(f"Unable to open SPI device after {i} retries")
                
        atexit.register(self.atexit)

    @command
    def xfer(self, data):
        return self.dev.transfer(data)
        
    def atexit(self):
        self.detach()
        
    def detach(self):
        self.dev = None
        
        output.debug(f"Tearing down SPI device {self.bus_no}.{self.dev_no}")
        
        spidev_unbind = open("/sys/bus/spi/drivers/spidev/unbind", "w")

        print(f"spi{self.bus_no}.{self.dev_no}", file=spidev_unbind)

        with open(self.override_file, "w") as f:
            print("spidev", file=f)
                
