import os
import time

from pathlib import Path

from piradio.devices.uio import UIO


class StreamFIR(UIO):
    def __init__(self, name):
        with open(f"/sys/firmware/devicetree/base/__symbols__/{name}", "r") as f:
            busname, addr = f.read()[:-1].split("@")

        busname = busname.split("/")[-1]

        p = Path(f"/sys/bus/platform/devices/{addr}.{busname}")

        os.system(f"sudo sh -c 'echo uio_pdrv_genirq > {p}/driver_override'")
        os.system(f"sudo sh -c 'echo $(basename {p}) > /sys/bus/platform/drivers_probe'")

        time.sleep(0.1)
        
        super().__init__(p)

        self.csr = self.maps[0]

        self.csr.map()
