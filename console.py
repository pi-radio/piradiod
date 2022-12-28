#!/usr/bin/env python3
import os
import sys

from board_140GHz import PiRadio_140GHz_Bringup, FW
from zcu111 import ZCU111
from picommand import PiCommandObject, picommand, command_loop


def check_spidev():
    with open("/proc/modules", "r") as f:
        for l in f:
            if "spidev" in l:
                return True
    return False

def startup():
    with open("/sys/class/fpga_manager/fpga0/state", "r") as f:
        if f.read().strip() != "operating":
            print("FPGA not programmed")
            sys.exit(1)
    
    if not check_spidev():
        if os.system("modprobe spidev") != 0:
            print("Unable to load spidev module")
            sys.exit(1)

    

class PiCommandRoot(PiCommandObject):
    def __init__(self):
        self.children.board = PiRadio_140GHz_Bringup()
        self.children.zcu111 = ZCU111()

if __name__ == '__main__':
    startup()
    
    root = PiCommandRoot()
        
    command_loop(root)      
