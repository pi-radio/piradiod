import mmap
import resource

from pathlib import Path

from piradio.output import output
from piradio.command import CommandObject, command

class UIOMap:
    def __init__(self, UIO, n, addr, offset, size):
        self.UIO = UIO
        self.n = n
        self.addr = addr
        self.offset = offset
        self.size = size

    def map(self):
        output.debug(f"Mapping map {self.n} size {self.size} addr {self.addr}")
        self.mmap = mmap.mmap(self.UIO.f.fileno(), self.size,
                              flags = mmap.MAP_SHARED,
                              prot = mmap.PROT_WRITE | mmap.PROT_READ,
                              offset=self.n * resource.getpagesize())

    def __getitem__(self, n):
        return self.mmap[n]

    def __setitem__(self, n, v):
        self.mmap[n] = v

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
            
            
        self.f = open(Path("/dev")/self.uio_name.stem, "r+")

