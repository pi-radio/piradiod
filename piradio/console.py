#!/usr/bin/env python3
import os
import sys
import click
    

@click.command()
@click.argument("board_type")
def start_console(board_type):
    if os.geteuid() != 0:
        print("Must be run as super-user")
        sys.exit(1)

    from piradio.zcu111 import ZCU111
    from piradio import boards
    from piradio.command import CommandObject, command, command_loop


    class CommandRoot(CommandObject):
        def __init__(self, board):
            self.children.board = board()
            self.children.zcu111 = ZCU111()

    def check_spidev():
        with open("/proc/modules", "r") as f:
            for l in f:
                if "spidev" in l:
                    return True
        return False



        
    with open("/sys/class/fpga_manager/fpga0/state", "r") as f:
        if f.read().strip() != "operating":
            print("FPGA not programmed")
            sys.exit(1)
    
    if not check_spidev():
        if os.system("modprobe spidev") != 0:
            print("Unable to load spidev module")
            sys.exit(1)

    try:
        bcls = getattr(boards, board_type)
    except Exception as e:
        print(f"Unable to find board {board_type}")
        raise e
        sys.exit(1)
        
    root = CommandRoot(bcls)

    command_loop(root)
