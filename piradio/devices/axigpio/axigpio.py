import os

import gpiod

from gpiod.line import Direction, Value

from piradio.output import output
from piradio.command import CommandObject, command, cmdproperty
from piradio.devices.sysfs import SysFS

class GPIOPin(CommandObject):
    def __init__(self, ctrl, n):
        self.n = n
        self.ctrl = ctrl

    @property
    def request(self):
        config = {
            self.n: gpiod.LineSettings(direction=self.dir)
        }

        return self.ctrl.chip.request_lines(config)

class InputPin(GPIOPin):
    def __init__(self, ctrl, n):
        super().__init__(ctrl, n)

    @property
    def dir(self):
        return Direction.INPUT
        
    @property
    def val(self):
        with self.request as r:
            return r.get_value(self.n)

class OutputPin(GPIOPin):
    def __init__(self, ctrl, n):
        super().__init__(ctrl, n)

    @property
    def dir(self):
        return Direction.OUTPUT
        
    @property
    def val(self):
        with self.request as r:
            return r.get_value(self.n)

    @val.setter
    def val(self, v):
        with self.request as r:
            return r.set_values({self.n: Value.ACTIVE if v else Value.INACTIVE})

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
        
        self.chip = gpiod.Chip(f"/dev/gpiochip{self.gpion}") #, gpiod.chip.OPEN_BY_NUMBER)
        
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
            
