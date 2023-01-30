import os

from piradio.command import CommandObject, command
from piradio.devices.sysfs import SysFS

class GPIOPin(CommandObject):
    IN = 0
    OUT = 1
    
    def __init__(self, ctrl, n):
        self.ctrl = ctrl
        self.n = self.ctrl.gpion + n

    @property
    def basepath(self):
        return self.ctrl.gpio_path / f"gpio{self.n}"
        
    @property
    def dirpath(self):
        return self.basepath / "direction"
        
    @property
    def valpath(self):
        return self.basepath / "value"

    @property
    def dir(self):
        print(self.dirpath)
        with open(self.dirpath, "r") as f:
            s = f.readline().strip()
            print(s)
            print(self.dirpath)
            if s == "out":
                return self.OUT
            assert s == "in", f"{s} is an invalid direction"
            return self.IN

    @dir.setter
    def dir(self, v):
        with open(self.dirpath, "w") as f:
            if v == self.IN or v.lower() == "in":
                f.write("in")
            elif v == self.OUT or v.lower() == "out":
                f.write("out")
            else:
                raise RuntimeError("Invalid direction")

    @property
    def val(self):
        with open(self.valpath, "r") as f:
            return int(f.read().strip())

    @val.setter
    def val(self, v):
        with open(self.valpath, "w") as f:
            f.write(f"{v}")
        
        
class AXI_GPIO(CommandObject):
    def __init__(self, name):
        devpath = SysFS.find_device(name)

        l = list((devpath / "gpio").iterdir())

        assert(len(l) == 1)

        chippath = l[0]

        assert chippath.stem.startswith("gpiochip")

        self.gpion = int(chippath.stem[len("gpiochip"):])

        self.gpio_path = chippath / "subsystem"
            
        for i in range(32):
            try:
                with open(self.gpio_path / "export", "w") as f:
                    f.write(f"{self.gpion + i}\n")
            except OSError as e:
                if e.errno == 16:
                    continue
                print(e)
        
    def __getitem__(self, n):
        return GPIOPin(self, n)
            
