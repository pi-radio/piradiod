import os

import gpiod

from piradio.output import output
from piradio.command import CommandObject, command, cmdproperty
from piradio.devices.sysfs import SysFS

class GPIOPin(CommandObject):
    IN = 0
    OUT = 1
    
    def __init__(self, ctrl, n):
        self.line = line
        
    @cmdproperty
    def dir(self):
        with open(self.dirpath, "r") as f:
            s = f.readline().strip()
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

    @cmdproperty
    def val(self):
        with open(self.valpath, "r") as f:
            s = f.read().strip()
            return int(s)

    @val.setter
    def val(self, v):
        with open(self.valpath, "w") as f:
            f.write(f"{v}\n")


class InputPin(CommandObject):
    def __init__(self, ctrl, n):
        config = gpiod.line_request()
        config.consumer = "piradio"
        config.request_type = gpiod.line_request.DIRECTION_INPUT

        self.line = ctrl.chip.get_line(n)
        self.line.request(config)

    @cmdproperty
    def val(self):
        return self.line.get_value()
        
class OutputPin(CommandObject):
    def __init__(self, ctrl, n):
        config = gpiod.line_request()
        config.consumer = "piradio"
        config.request_type = gpiod.line_request.DIRECTION_OUTPUT
        
        self.line = ctrl.chip.get_line(n)
        self.line.request(config)

    @cmdproperty
    def val(self):
        return self.line.get_value()

    @val.setter
    def val(self, v):
        self.line.set_value(v)

_gpios = {}
        
class AXI_GPIO(CommandObject):
    def __new__(cls, name):
        if name in _gpios:
            return _gpios[name]

        _gpios[name] = super().__new__(cls)

        _gpios[name].__init__(name)

        return _gpios[name]
        
    def __init__(self, name):
        devpath = SysFS.find_device(name)

        l = list(devpath.glob("gpiochip*"))
        
        assert len(l) == 1, f"Too many gpiochip entires: {l}"

        chippath = l[0]

        self.gpion = int(chippath.stem[len("gpiochip"):])

        output.debug(f"Opening GPIO chip {self.gpion} {chippath}")
        
        self.chip = gpiod.chip(self.gpion) #, gpiod.chip.OPEN_BY_NUMBER)
        
        self.gpio_path = chippath / "subsystem"

        self.pins = {}
        
        class Inputs(CommandObject):
            def __getitem__(cls, n):
                if n in self.pins:
                    if not isinstance(self.pins[n], InputPin):
                        raise RuntimeError(f"Pin {n} already opened as output")
                    return self.pins[n]

                self.pins[n] = InputPin(self, n)
                return self.pins[n] 

        class Outputs(CommandObject):
            def __getitem__(cls, n):
                if n in self.pins:
                    if not isinstance(self.pins[n], OutputPin):
                        raise RuntimeError(f"Pin {n} already opened as output")
                    return self.pins[n]

                self.pins[n] = OutputPin(self, n)
                return self.pins[n] 

        self.children.inputs = Inputs()
        self.children.outputs = Outputs()
    
    def __getitem__(self, n):
        return self.pins[n]
            
