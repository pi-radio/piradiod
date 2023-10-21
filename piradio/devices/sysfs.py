from pathlib import Path
from piradio.output import output

sysfs_dt_path = Path("/sys/firmware/devicetree/base")
sysfs_devices_path = Path("/sys/devices/platform")

class SysFS:
    @classmethod
    def find_device(cls, name):
        p = sysfs_dt_path / "__symbols__" / name

        with open(p, "r") as f:
            dev = f.read()[1:-1]

        _, dev = dev.split("/")
        dev, addr = dev.split("@")
            
        output.debug(f"dev: {dev} addr: {addr}")

        l = list((sysfs_devices_path / "axi").glob(f"{addr}.*"))

        assert len(l) == 1

        return l[0]
