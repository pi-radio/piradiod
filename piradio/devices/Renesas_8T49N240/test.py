#!/usr/bin/env python3
import time
import glob
import itertools
from pathlib import Path

from periphery import I2C
from periphery.i2c import I2CError


i2c = I2C("/dev/i2c-23")

class Renesas_8T49N240:
    addr=0x6c

    """
    0000–0001Startup Control Registers
    0002–0005Device ID Control Registers
    0006–0007Serial Interface Control Registers
    0008–002FDigital PLL Control Registers
    0030–0038GPIO Control Registers
    0039–003EOutput Driver Control Registers
    003F–004AOutput Divider Control Registers (Integer Portion)
    004B–0056Reserved
    0057–0062Output Divider Control Registers (Fractional Portion)
    0063–0067Output Divider Source Control Registers
    0068–006CAnalog PLL Control Registers
    006D–0070Power-Down and Lock Alarm Control Registers
    0071–0078Input Monitor Control Registers
    0079Interrupt Enable Register
    007A–007BReserved
    007C–01FFReserved
    0200–0201Interrupt Status Registers
    0202–020BReserved
    020CGeneral-Purpose Input Status Register
    020D–0211Global Interrupt and Boot Status Register
    0212–03FFReserved
    """

    valid_regs = itertools.chain(
        range(0x4B), range(0x57, 0x7A), range(0x200, 0x202), range(0x20C, 0x212)
    )
    

    prog1 = [
        0x09, 0x50, 0x00, 0x60, 0xc0, 0x01, 0x6c, 0x01,
        0x03, 0x00, 0x20, 0x00, 0x01, 0x39, 0x00, 0x00,
        0x01, 0x00, 0x4d, 0x07, 0x07, 0x00, 0x00, 0x77,
        0x6d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff,
        
        0xff, 0xff, 0xff, 0x03, 0x3f, 0x00, 0x19, 0x00,
        0x06, 0x66, 0x66, 0x00, 0x01, 0x00, 0x00, 0xd0,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x03, 0x00, 0x00, 0x00, 0x44, 0x44, 0x38,
        
        0x00, 0x02, 0x38, 0x00, 0x02, 0x00, 0x00, 0x03,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x2a, 0x06, 0x2b, 0x20, 0x09, 0x00, 0x00, 0x0c,
        0x00, 0x00, 0x00, 0x0b, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x27, 0xcc, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        0x00, 0x00, 0x00, 0x00, 0x85, 0x00, 0x00, 0x9c,
        0x01, 0xd4, 0x02, 0x71, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x83, 0x00, 0x10, 0x02, 0x08, 0x8c
    ]


    SDRv2Config = {
        0x000: 0x09,
        0x001: 0x50,
        0x002: 0x00,
        0x003: 0x60,
        0x004: 0xc0,
        0x005: 0x01,
        0x006: 0x6c,
        0x007: 0x01,
        0x008: 0x03,
        0x009: 0x00,
        0x00a: 0x20,
        0x00b: 0x00,
        0x00c: 0x01,
        0x00d: 0x39,
        0x00e: 0x00,
        0x00f: 0x00,
        0x010: 0x01,
        0x011: 0x00,
        0x012: 0x4d,
        0x013: 0x07,
        0x014: 0x07,
        0x015: 0x00,
        0x016: 0x00,
        0x017: 0x77,
        0x018: 0x6d,
        0x019: 0x00,
        0x01a: 0x00,
        0x01b: 0x00,
        0x01c: 0x00,
        0x01d: 0x00,
        0x01e: 0x00,
        0x01f: 0xff,
        0x020: 0xff,
        0x021: 0xff,
        0x022: 0xff,
        0x023: 0x03,
        0x024: 0x3f,
        0x025: 0x00,
        0x026: 0x19,
        0x027: 0x00,
        0x028: 0x06,
        0x029: 0x66,
        0x02a: 0x66,
        0x02b: 0x00,
        0x02c: 0x01,
        0x02d: 0x00,
        0x02e: 0x00,
        0x02f: 0xd0,
        0x030: 0x00,
        0x031: 0x00,
        0x032: 0x00,
        0x033: 0x00,
        0x034: 0x00,
        0x035: 0x00,
        0x036: 0x00,
        0x037: 0x00,
        0x038: 0x00,
        0x039: 0x03,
        0x03a: 0x00,
        0x03b: 0x00,
        0x03c: 0x00,
        0x03d: 0x44,
        0x03e: 0x44,
        0x03f: 0x38,
        0x040: 0x00,
        0x041: 0x02,
        0x042: 0x38,
        0x043: 0x00,
        0x044: 0x02,
        0x045: 0x00,
        0x046: 0x00,
        0x047: 0x03,
        0x048: 0x00,
        0x049: 0x00,
        0x04a: 0x00,
        0x057: 0x00,
        0x058: 0x00,
        0x059: 0x00,
        0x05a: 0x00,
        0x05b: 0x00,
        0x05c: 0x00,
        0x05d: 0x00,
        0x05e: 0x00,
        0x05f: 0x00,
        0x060: 0x00,
        0x061: 0x00,
        0x062: 0x00,
        0x063: 0x00,
        0x064: 0x00,
        0x065: 0x00,
        0x066: 0x00,
        0x067: 0x00,
        0x068: 0x2a,
        0x069: 0x06,
        0x06a: 0x2b,
        0x06b: 0x20,
        0x06c: 0x09,
        0x06d: 0x00,
        0x06e: 0x00,
        0x06f: 0x0c,
        0x070: 0x00,
        0x071: 0x00,
        0x072: 0x00,
        0x073: 0x0b,
        0x074: 0x00,
        0x075: 0x00,
        0x076: 0x00,
        0x077: 0x00,
        0x078: 0x00,
        0x079: 0x00,
        0x200: 0x53,
        0x201: 0x00,
        0x20c: 0x00,
        0x20d: 0x00,
        0x20e: 0x00,
        0x20f: 0x00,
        0x210: 0x00,
        0x211: 0x00,
    }
        
    def __init__(self):
        with open("/sys/class/gpio/gpio286/value", "w") as f:
            f.write("0\n")

        time.sleep(0.5)
            
        with open("/sys/class/gpio/gpio286/value", "w") as f:
            f.write("1\n")

        time.sleep(0.5)
        
        f = Path("/dev") / list(Path("/sys/bus/platform/devices").glob("a*.i2c/i2c-*"))[0].stem

        self.i2c = I2C(f)

        data = self.read_reg(0, 10)

        self.rev_id = data[2] >> 4
        self.dev_id = ((data[2] & 0xF) << 12) | (data[3] << 4) | ((data[4] & 0xF0) >> 4)
        self.dash_code = ((data[4] & 0xF) << 7) | (data[5] >> 1)

        assert self.dev_id == 0x60C, f"Invalid ID code received {self.dev_id}"
        assert data[5] & 1

        start_addr = 0
        nregs = 0
        d = []

        if False:
            for addr in sorted(self.SDRv2Config.keys()):
                reg_val = self.SDRv2Config[addr]

                assert self.prog1[addr] == reg_val

                if addr < 8:
                    continue

                if addr != start_addr + nregs:
                    if nregs:
                        self.write_reg(start_addr, d)
                    start_addr = addr
                    nregs = 0
                    d = []

                nregs += 1
                d.append(self.SDRv2Config[addr])
        else:
            start_addr = 8
            d = self.prog1[8:]
            nregs = len(self.prog1[8:])
                
        if nregs:
            self.write_reg(start_addr, d)
            
        for i in range(5):
            time.sleep(1)
            print(f"Locked: {self.locked}")
            
        print(f"{self.read_reg(0x200):x}")
        self.write_reg(0x200, 0x53)
        print(f"{self.read_reg(0x200):x}")

    @property
    def locked(self):
        v = self.read_reg(0x203)

        return ((v >> 4) & 1) == 1
        
    def read_reg(self, reg, nreg = 1):
        msg = [ I2C.Message([ (reg >> 8) & 0xFF, reg & 0xFF ]), I2C.Message([ 0x00 ] * nreg, read=True) ]

        self.i2c.transfer(self.addr, msg)

        if nreg == 1:
            return msg[1].data[0]
        
        return msg[1].data

    def write_reg(self, reg, val):
        if isinstance(val, list):
            msg = [ I2C.Message([ (reg >> 8) & 0xFF, reg & 0xFF, *val ]) ]
        else:
            msg = [ I2C.Message([ (reg >> 8) & 0xFF, reg & 0xFF, val ]) ]

        self.i2c.transfer(self.addr, msg)

r = Renesas_8T49N240()

