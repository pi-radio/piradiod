import mmap
import inspect
import resource
import struct
import os

from pathlib import Path

from piradio.output import output
from piradio.command import CommandObject, command

class RegisterTreeObject:
    def __init__(self):
        self.regs = dict()
        for k, v in inspect.get_annotations(type(self)).items():
            if hasattr(v, "__uio__"):                
                self.regs[k] = v
                
    def __getattr__(self, name):
        if name in self.regs:
            return self.regs[name].get(self, name)
    
        raise AttributeError(f"{name} not defined")

    def __setattr__(self, name, val):
        if 'regs' not in self.__dict__:
            return super().__setattr__(name, val)
        
        if name in self.regs:
            self.regs[name].set(self, name, val)
            return

        super().__setattr__(name, val)

class reg_inst:
    __uio__ = True
    def __init__(self, obj, offset):
        self.obj = obj
        self.offset = offset


        
class reg:
    __uio__ = True
    def __init__(self, offset):
        self.offset = offset

    def __get__(self, obj, objtype):
        print("reg get")

    def get(self, obj, name):
        return obj.csr[self.offset >> 2]

    def set(self, obj, name, val):
        obj.csr[self.offset >> 2] = val
        
    def attach(self, obj):
        return reg_inst(obj, self.offset)

    
class window_inst(RegisterTreeObject):
    __uio__ = True
    def __init__(self, obj, window):        

        super().__init__()
        self.regs = window.regs
        self.window = window
        self.obj = obj

    @property
    def csr(self):
        return self

    def __getitem__(self, n):
        return self.obj.csr[(self.window.offset >> 2) + n]

    def __setitem__(self, n, v):
        self.obj.csr[(self.window.offset >> 2) + n] = v

    
    def __repr__(self):
        return f"<Window {self.window.offset:x} {self.window.size:x}>"

    
class window(RegisterTreeObject):
    __uio__ = True
    def __init__(self, offset, size):
        super().__init__()
        self.offset = offset
        self.size = size

    def get(self, obj, name):
        return window_inst(obj, self)

    def __repr__(self):
        return f"<Abstract window {self.offset:x} {self.size:x}>"
        
class window_array_inst:
    __uio__ = True

    def __init__(self, obj, wa):
        self.obj = obj
        self.windows = list()

        offset = wa.offset

        for i in range(wa.n):
            w = window(offset, wa.size)
            w.regs = wa.regs
            
            self.windows.append(window_inst(obj, w))
            offset += wa.stride
            
    def __getitem__(self, i):
        return self.windows[i]

        
        
        
class window_array(RegisterTreeObject):
    __uio__ = True

    def __init__(self, offset, size, stride, n, obj=None):
        super().__init__()
        self.offset = offset
        self.size = size
        self.stride = stride
        self.n = n

    def get(self, obj, name):
        return window_array_inst(obj, self)
    

# Let's just assume 32-bit access
class UIOMap:
    def __init__(self, UIO, n, addr, offset, size):
        self.UIO = UIO
        self.n = n
        self.addr = addr
        self.offset = offset
        self.size = size

    def map(self):
        output.debug(f"Mapping map {self.n} size {self.size} addr {self.addr}")
        self.mmap = mmap.mmap(self.UIO.fd, self.size,
                              flags = mmap.MAP_SHARED,
                              prot = mmap.PROT_WRITE | mmap.PROT_READ,
                              offset=self.n * resource.getpagesize())
        self.mv = memoryview(self.mmap)
        self.mv32 = self.mv.cast('I')
        
    def __getitem__(self, n):
        return self.mv32[n]

    def __setitem__(self, n, v):
        self.mv32[n] = v

uint32 = struct.Struct("I")


class UIO(CommandObject):
    def __init__(self, path, attach=False):
        self.path = path

        l = list((self.path / "uio").glob("uio*"))

        if len(l) > 1:
            raise RuntimeError("Too many uio nodes in directory")
        
        if len(l) == 1:
            self.uio_name = l[0]
        elif attach:
            output.debug(f"Overriding driver for {self.path}")
            with open(self.path / "driver_override", "w") as f:
                print("uio_pdrv_genirq", file=f)

            with open("/sys/bus/platform/drivers_probe", "w") as f:
                print(f"{self.path.name}", file=f)
                
            l = list((self.path / "uio").glob("uio*"))
            
            self.uio_name = l[0]
        else:
            raise RuntimeError(f"No uio node found for {self.path}")
        
        
        maps_path = Path("/sys/class/uio") / self.uio_name / "maps"

        self.maps = []
        
        output.debug(f"uio: {self.path} Maps: {maps_path}")

        self.fd = os.open(Path("/dev")/self.uio_name.stem, os.O_RDWR | os.O_SYNC | os.O_NONBLOCK)
        
        for p in maps_path.glob("map*"):
            n = int(p.stem[3:])
                              
            with open(p / "addr") as f:
                addr = int(f.read().strip(), 16)

            with open(p / "offset") as f:
                offset = int(f.read().strip(), 16)
                
            with open(p / "size") as f:
                size = int(f.read().strip(), 16)

            output.debug(f"{p.stem}: 0x{addr:x} 0x{offset:x} 0x{size:x}")
            self.maps.append(UIOMap(self, n, addr, offset, size))

        self.regs = {}
            
        for k, v in inspect.get_annotations(type(self)).items():
            if hasattr(v, "__uio__"):                
                self.regs[k] = v

    def __getattr__(self, name):
        if name == 'regs':
            return self.regs

        if name in self.regs:
            return self.regs[name].get(self, name)
    
        raise AttributeError(f"{name} not defined")

    def __setattr__(self, name, val):
        if 'regs' not in self.__dict__:
            return super().__setattr__(name, val)
        
        if name in self.regs:
            self.regs[name].set(self, name, val)
            return

        super().__setattr__(name, val)
