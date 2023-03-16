#!/usr/bin/env python3
import os
import sys
import click

from io import BytesIO, StringIO

import numpy as np
from numpy.lib import format as npf

import matplotlib.pyplot as plt

from twisted.web import xmlrpc, server
from twisted.internet import reactor, endpoints

from piradio.zcu111 import zcu111
from piradio import boards
from piradio.command import CommandObject, command, command_loop, task_manager

class PiRadioXMLRPC(xmlrpc.XMLRPC):
    def __init__(self, root_obj):
        self.root_obj = root_obj
        super().__init__(allowNone=True)

    def xmlrpc_get_samples(self, direction, n):
        if n < 0 or n > 7:
            raise xmlrpc.Fault(123, "Invalid buffer number")
        
        if direction == 'input':
            f = BytesIO()
            npf.write_array(f, self.root_obj.board.input_samples[n].capture())
            return f.getvalue()
        elif direction == 'output':
            return self.root_obj.board.output_samples[n].capture()
        else:
            raise xmlrpc.Fault(123, "Invalid direction")
        
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
    if os.geteuid() != 0:
        print("Must be run as super-user")
        sys.exit(1)
    
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

    rpc = PiRadioXMLRPC(root)

    endpoint = endpoints.TCP4ServerEndpoint(reactor, 7777)
    endpoint.listen(server.Site(rpc))

    reactor.callInThread(command_loop, root)
    reactor.run()
    
    print("Exiting all tasks")
    task_manager.stop_all()

if __name__ == "__main__":
    start_console()
