#!/usr/bin/env python3

import time

from MAX11300 import MAX11300Dev

for i in range(8, 12):
    try:
        dev = MAX11300Dev(2, i)
    except Exception as e:
        print(e)
        continue
