#!/usr/bin/env python3
import glob

from periphery import I2C
from periphery.i2c import I2CError

from piradio.devices import Si5382
from piradio.devices import LMK04208
from piradio.devices import RFDC

from piradio.command import CommandObject, command

regs_4GHz = [
    0x700000, 0x6f0000, 0x6e0000, 0x6d0000,
    0x6c0000, 0x6b0000, 0x6a0000, 0x690021,
    0x680000, 0x670000, 0x663f80, 0x650011,
    0x640000, 0x630000, 0x620200, 0x610888,
    0x600000, 0x5f0000, 0x5e0000, 0x5d0000,
    0x5c0000, 0x5b0000, 0x5a0000, 0x590000,
    0x580000, 0x570000, 0x560000, 0x55d300,
    0x540001, 0x530000, 0x521e00, 0x510000,
    0x506666, 0x4f0026, 0x4e0003, 0x4d0000,
    0x4c000c, 0x4b0800, 0x4a0000, 0x49003f,
    0x480001, 0x470081, 0x46c350, 0x450000,
    0x4403e8, 0x430000, 0x4201f4, 0x410000,
    0x401388, 0x3f0000, 0x3e0322, 0x3d00a8,
    0x3c0000, 0x3b0001, 0x3a8001, 0x390020,
    0x380000, 0x370000, 0x360000, 0x350000,
    0x340820, 0x330080, 0x320000, 0x314180,
    0x300300, 0x2f0300, 0x2e07fc, 0x2dc0cc,
    0x2c0c23, 0x2b0005, 0x2a0000, 0x290000,
    0x280000, 0x270030, 0x260000, 0x250304,
    0x240041, 0x230004, 0x220000, 0x211e21,
    0x200393, 0x1f03ec, 0x1e318c, 0x1d318c,
    0x1c0488, 0x1b0002, 0x1a0db0, 0x190624,
    0x18071a, 0x17007c, 0x160001, 0x150401,
    0x14e048, 0x1327b7, 0x120064, 0x11012c,
    0x100080, 0x0f064f, 0x0e1e70, 0x0d4000,
    0x0c5001, 0x0b0018, 0x0a10d8, 0x090604,
    0x082000, 0x0740b2, 0x06c802, 0x0500c8,
    0x040a43, 0x030642, 0x020500, 0x010808,
    0x00249c ]


SCI18IS602Addr=0x2f
LMXAddrs = [ 0x08, 0x04, 0x01 ]


class ZCU111(CommandObject):
    def __init__(self):
        self.children.Si5382 = Si5382()
        self.children.LMK04208 = LMK04208()
        self.children.rfdc = RFDC()

        
    @command
    def program(self):
        self.children.Si5382.program()
        self.children.LMK04208.program()
        
        print("Configuring LMX2594s")

        for p in glob.glob("/dev/i2c-*"):
            i2c = I2C(p)
            try:
                msgs = [ I2C.Message([0x00], read=True) ]
                i2c.transfer(SCI18IS602Addr, msgs)
                print(f"Found on bus {p}")
            except I2CError as e:
                continue

            for lmx in LMXAddrs:
                print(f"Programming LMX@{lmx}...");
                for r in regs_4GHz:
                    try:
                        msgs = [ I2C.Message([ lmx,
                                               (r >> 16) & 0xFF, (r >> 8) & 0xFF, (r) & 0xFF ])]
                        i2c.transfer(SCI18IS602Addr, msgs)
                    except I2CError as e:
                        print(f"Error in transfer {s}: {e}")
                        continue

zcu111 = ZCU111()
