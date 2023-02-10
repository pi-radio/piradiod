import mmap
import resource
import struct
import os

from pathlib import Path

from piradio.output import output
from piradio.command import CommandObject, command

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


class UIOWindow:
    def __init__(self, offset, obj=None):
        self.offset = offset
        self.obj = obj
        
    def __get__(self, obj, objtype):
        return self.__class__(self.offset, obj)

    @property
    def csr(self):
        print("Getting Window CSR")
        class CSR:
            def __getitem__(csr, a):
                return self.obj.csr[self.offset + a]

            def __getitem__(csr, a, v):
                self.obj.csr[self.offset + a] = v

            
class UIORegister:
    def __init__(self, offset):
        self.offset = offset // 4

    def __get__(self, obj, objtype):
        print(f"UIO Reg: {self.offset}")
        return obj.csr[self.offset]

    def __set__(self, obj, v):
        obj.csr[self.offset] = v


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
            
            

