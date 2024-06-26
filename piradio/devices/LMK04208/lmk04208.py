#!/usr/bin/env python3
import glob
import time

from periphery import I2C
from periphery.i2c import I2CError

from piradio.command import CommandObject, command

SCI18IS602Addr=0x2f
LMKAddr = 0x02

prog_seq = [
    [0x00, 0x16, 0x00, 0x40],
    [0x20, 0x14, 0x30, 0x00],
    [0x00, 0x14, 0x30, 0x01],
    [0x00, 0x14, 0x03, 0x02],
    [0xC0, 0x14, 0x00, 0x23],
    [0x40, 0x14, 0x00, 0x24],
    [0x80, 0x14, 0x1E, 0x05],
    [0x01, 0x10, 0x00, 0x06],
    [0x01, 0x10, 0x00, 0x07],
    [0x06, 0x01, 0x00, 0x08],
    [0x55, 0x55, 0x55, 0x49],
    [0x91, 0x02, 0x41, 0x0A],
    [0x04, 0x01, 0x10, 0x0B],
    [0x1B, 0x0C, 0x00, 0x6C],
    [0x23, 0x02, 0x80, 0x6D],
    [0x02, 0x00, 0x00, 0x0E],
    [0x80, 0x00, 0x80, 0x0F],
    [0xC1, 0x55, 0x04, 0x10],
    [0x00, 0x00, 0x00, 0x58],
    [0x02, 0xC9, 0xC4, 0x19],
    [0x8F, 0xA8, 0x00, 0x1A],
    [0x10, 0x00, 0x1E, 0x1B],
    [0x00, 0x21, 0x20, 0x1C],
    [0x01, 0x80, 0x03, 0x1D],
    [0x02, 0x00, 0x03, 0x1E],
    [0x00, 0x3F, 0x00, 0x1F],
]

class LMK04208:
    def __init__(self):
        self.i2c = None

        for p in glob.glob("/dev/i2c-*"):
            i2c = I2C(p)
            try:
                msgs = [ I2C.Message([0x00], read=True) ]
                i2c.transfer(SCI18IS602Addr, msgs)
                self.i2c = i2c
                break
            except I2CError as e:
                continue

        if self.i2c is None:
            raise RuntimeError("Unable to find LMK04208")
            
    @command
    def program(self):
        for s in prog_seq:
            try:
                msgs = [ I2C.Message([ LMKAddr ] + s) ]
                self.i2c.transfer(SCI18IS602Addr, msgs)
            except I2CError as e:
                print(f"Error in transfer {s}: {e}")
                continue
