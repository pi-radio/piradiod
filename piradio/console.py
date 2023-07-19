#!/usr/bin/env python3
import os
import sys
import click

from io import BytesIO, StringIO

import matplotlib.pyplot as plt

from twisted.web import xmlrpc, server
from twisted.internet import reactor, endpoints

from piradio import zcu111
from piradio import boards
from piradio.command import CommandObject, command, command_loop, task_manager

        
class CommandRoot(CommandObject):        
    def __init__(self, board):
        self.children.board = board()
        self.children.zcu111 = zcu111


def check_spidev():
    with open("/proc/modules", "r") as f:
        for l in f:
            if "spidev" in l:
                return True
    return False
        
def initial_setup():
    with open("/sys/class/fpga_manager/fpga0/state", "r") as f:
        if f.read().strip() != "operating":
            print("FPGA not programmed")
            sys.exit(1)
    
    if not check_spidev():
        if os.system("modprobe spidev") != 0:
            print("Unable to load spidev module")
            sys.exit(1)

@click.command()
@click.argument("board_type")
def start_console(board_type):
    initial_setup()

    try:
        bcls = getattr(boards, board_type)
    except Exception as e:
        print(f"Unable to find board {board_type}")
        raise e
        sys.exit(1)

    root = CommandRoot(bcls)
        
    try:
        command_loop(root)
    except:
        print("Exiting all tasks")
        task_manager.stop_all()

if __name__ == "__main__":
    start_console()
