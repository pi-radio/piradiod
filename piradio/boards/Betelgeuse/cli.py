from .betelgeuse import Betelgeuse

import click


@click.group()
def cli():
    pass


@cli.command()
def startup():
    bg = Betelgeuse()

    for port in bg.ports:
        port.set_adc_gain(21)
        port.set_dac1_gain(21)
        port.set_dac2_gain(12)
    
