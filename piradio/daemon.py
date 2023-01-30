#!/usr/bin/env python3
import os
import sys
import click
import twisted

from piradio.zcu111 import ZCU111
from piradio import board
from piradio.command import CommandObject, command, command_loop



@click.command()
@click.argument("board_type")
def main(board_type):
    pass
