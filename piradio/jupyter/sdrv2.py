import sys
import time
from piradio.boards import SDRv2
from piradio.util import Freq, MHz, GHz, Samples

from .nrt import *

board = SDRv2()
board.reset()


capture()
prcaptures = [ Samples(sbi) for sbi in sbis ]

def rescan_radios():
    board.detect_radios()
    
    for radio, sbi, sbo in zip(board.radios, sbis, sbos):
        if radio is None:
            continue

        radio.sbi = sbi
        radio.sbo = sbo
    
        
rescan_radios()

