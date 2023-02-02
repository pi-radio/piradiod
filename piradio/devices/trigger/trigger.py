import math
import struct
from pathlib import Path
from functools import cached_property

from piradio.output import output
from piradio.command import command
from piradio.devices.uio import UIO, UIO_CSR

dt_uint32 = struct.Struct(">i")

uint32 = struct.Struct("i")
csr_struct = struct.Struct("iiiiii")


class Trigger(UIO):
    def __init__(self):
        l = list(Path("/sys/bus/platform/devices").glob("*.piradip_trigger_unit"))

        assert len(l) == 1, "Only set up for one trigger unit at the moment"

        path = l[0]

        super().__init__(path, attach=True)
        
        self.csr = UIO_CSR(self.maps[0])

        assert self.csr[0] == 0x50545247, "Improper IP ID"
        
        print(f"{self.csr[0]:x}")
        
        class DelayMap:
            trigger = self
            DELAY_MAP_BASE = 3

            def __getitem__(self, n):
                return self.trigger.csr[self.DELAY_MAP_BASE + n]

            def __setitem__(self, n, v):
                self.trigger.csr[self.DELAY_MAP_BASE + n] = v

        class EnableMap:
            trigger = self

            def __getitem__(self, n):
                return True if (self.trigger.csr[1] >> n) & 1 == 1 else False

            def __setitem__(self, n, v):
                if v:
                    self.trigger.csr[1] |= (1 << n)
                else:
                    self.trigger.csr[1] &= ~(1 << n)

        self._delays = DelayMap()
        self._enables = EnableMap()

        
    @property
    def delays(self):
        return self._delays
        
    @property
    def enables(self):
        return self._enables

    def enable_all(self):
        self.trigger.csr[1] = 0xFFFFFFFF

    def trigger(self):
        self.trigger.csr[2] = 0
        
    
