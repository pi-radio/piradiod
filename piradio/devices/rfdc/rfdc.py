import math
import struct
from pathlib import Path
from functools import cached_property
from multiprocessing import Process

import numpy as np
import matplotlib.pyplot as plt

from piradio.output import output
from piradio.command import command
from piradio.devices.uio import UIO, UIOWindow, UIORegister

from .adc import ADCTile
from .dac import DACTile




        
class RFDC(UIO):
    DACTiles = [ DACTile(0x04000 + 0x4000 * i, 0x4000) for i in range(4) ]
    ADCTiles = [ DACTile(0x14000 + 0x4000 * i, 0x4000) for i in range(4) ]

    IP_VERSION = UIORegister(0x0000)
    MASTER_RESET = UIORegister(0x0004)
    CISR = UIORegister(0x0008)
    CIER = UIORegister(0x000C)

    XRFDC_TILES_ENABLED_OFFSET = UIORegister(0x00A0) # The tiles enabled in the design
    XRFDC_ADC_PATHS_ENABLED_OFFSET = UIORegister(0x00A4) # The ADC analogue/digital paths enabled in the design
    XRFDC_DAC_PATHS_ENABLED_OFFSET = UIORegister(0x00A8) # The DAC analogue/digital paths enabled in the design */
    #define XRFDC_PATH_ENABLED_TILE_SHIFT 4U /**< A shift to get to the correct tile for the path */

    
    
    def __init__(self):
        path = None

        l = list(Path("/sys/bus/platform/devices").glob(f"*.usp_rf_data_converter"))

        assert len(l) == 1, f"Could not determine data converter path: {l}"

        path = l[0]

        output.info(f"Found RFDC at {path}")
                
        super().__init__(path, attach=True)
    
        self.csr = self.maps[0]

        self.csr.map()

        print(f"{self.csr[0]} {self.csr[1]} {self.csr[2]} {self.csr[3]}")

        self.status()
        
    @command
    def status(self):
        output.info(f"RFDC IP Version: {self.IP_VERSION}")
        output.info(f"Master Reset: {self.MASTER_RESET}")
        output.info(f"Interrupt Status: {self.CISR}")
        output.info(f"Interrupt Enable: {self.CIER}")
        
    @command
    def reset(self):
        self.MASTER_RESET = 1
