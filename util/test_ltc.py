#!/usr/bin/env python3

from LTC5584 import LTC5584Dev

for i in range(8):
    d = LTC5584Dev(2, i)

    print(d.read_reg(0x10))
