import math
import struct
from pathlib import Path
from functools import cached_property

from piradio.output import output
from piradio.command import command
from piradio.devices.uio import UIO

dt_uint32 = struct.Struct(">i")

uint32 = struct.Struct("i")
csr_struct = struct.Struct("iiiiii")


class Trigger(UIO):
    def __init__(self):
        l = list(Path("/sys/bus/platform/devices").glob("*.piradip_trigger_unit"))

        assert len(l) == 1, "Only set up for one trigger unit at the moment"

        path = l[0]

        super().__init__(path, attach=True)
        
        self.csr = self.maps[0]

        self.csr.map()
        
        assert self.csr[0] == 0x50545247, "Improper IP ID"
        
        class DelayMap:
            trigger = self
            DELAY_MAP_BASE = 3

            def __getitem__(self, n):
                return self.trigger.csr[4 * (self.DELAY_MAP_BASE + n)]

            def __setitem__(self, n, v):
                self.trigger.csr[4 * (self.DELAY_MAP_BASE + n)] = v

        class EnableMap:
            trigger = self

            def __getitem__(self, n):
                return True if (self.trigger.csr[4 * 1] >> n) & 1 == 1 else False

            def __setitem__(self, n, v):
                if v:
                    self.trigger.csr[4 * 1] |= (1 << n)
                else:
                    self.trigger.csr[4 * 1] &= ~(1 << n)

        self._delays = DelayMap()
        self._enables = EnableMap()

        for i in range(16):
            self.csr[4 * (3 + i)] = 1

        
    @property
    def delays(self):
        return self._delays
        
    @property
    def enables(self):
        return self._enables

    @command
    def enable_all(self):
        self.csr[4 * 1] = 0xFFFFFFFF

    @command
    def trigger(self):
        self.csr[4 * 2] = 0

    @command
    def status(self):
        print(f"IP id: {self.csr[0]:08x}")
        print(f"Enables: {self.csr[1]:08x}")
        print(f"Trigger: {self.csr[2]:08x}")

        for i in range(32):
            print(f"Delay {i}: {self.csr[3+i]}")
    
