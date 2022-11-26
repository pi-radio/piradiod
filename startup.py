#!/usr/bin/env python3

import os

os.system("../load140.sh")
os.system("sudo modprobe spidev")
os.system("sudo ./zcu111.py")
