#!/usr/bin/env python3
import time
import click


from MAX11300 import MAX11300Dev


@click.command()
@click.argument('voltage', type=float)
def setdac(voltage):
    d = MAX11300Dev(2, 8)

    d.port[0].dac = voltage

if __name__ == "__main__":
    setdac()
    
