#!/usr/bin/env python3

from LMX2595 import LMX2595Dev

LMXs = [ LMX2595Dev(2, i) for i in [ 12, 13, 14 ] ]

for l in LMXs:
    l.program()

