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

        config = {
            self.n: gpiod.LineSettings(direction=self.dir)
        }

        self.line = self.ctrl.chip.request_lines(config, consumer="piradio") 

class InputPin(GPIOPin):
    def __init__(self, ctrl, n):
        super().__init__(ctrl, n)

    @property
    def dir(self):
        return Direction.INPUT
        
    @property
    def val(self):
        return self.line.get_value(self.n)

class OutputPin(GPIOPin):
    def __init__(self, ctrl, n):
        super().__init__(ctrl, n)

    @property
    def dir(self):
        return Direction.OUTPUT
        
    @property
    def val(self):
        return self.line.get_value(self.n)

    @val.setter
    def val(self, v):
        v = Value.ACTIVE if v else Value.INACTIVE
        self.line.set_value(self.n, v)
            

_gpios = {}
        
class AXI_GPIO(CommandObject):
    def __new__(cls, name):
        print(f"__new__: {name} {_gpios}")
        if name in _gpios:
            return _gpios[name]

        _gpios[name] = super().__new__(cls)

        return _gpios[name]
        
    def __init__(self, name):
        if hasattr(self, "chip"):
            return
        
        devpath = SysFS.find_device(name)

        l = list(devpath.glob("gpiochip*"))
        
        assert len(l) == 1, f"Too many gpiochip entires: {l}"

        chippath = l[0]

        print(f"Opening GPIO {chippath}")
        
        self.chip = gpiod.Chip(f"/dev/{chippath.stem}")
        
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
            
