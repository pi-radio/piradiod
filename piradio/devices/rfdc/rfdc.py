import math
import struct
from pathlib import Path
from functools import cached_property
from multiprocessing import Process

import numpy as np
import matplotlib.pyplot as plt
from struct import Struct
from collections import namedtuple

from piradio.output import output
from piradio.command import command
from piradio.devices.uio import UIO, reg, window, window_array

from .config import RFDCConfigParams
from .adc import ADCBlock
from .dac import DACBlock
    
###
### Register map:
### 0x000000 - Base CSR
### 0x004000 - DAC Tile 0 CSR
###  0x004000 - Tile 0 Block 0 CSR
###  0x004400 - Tile 0 Block 1 CSR
###  ...
### 0x006000 - DAC 0 DRP
### 0x008000 - DAC 1 CSR
### ...
### 0x014000 - ADC 0 CSR
### 0x016000 - ADC 0 DRP
### 0x018000 - ADC 1 CSR

# BLOCK_BASE gives DRP base

"""
#define XRFDC_DAC_TILE_DRP_ADDR(X) (0x6000U + (X * 0x4000U))
#define XRFDC_DAC_TILE_CTRL_STATS_ADDR(X) (0x4000U + (X * 0x4000U))
#define XRFDC_ADC_TILE_DRP_ADDR(X) (0x16000U + (X * 0x4000U))
#define XRFDC_ADC_TILE_CTRL_STATS_ADDR(X) (0x14000U + (X * 0x4000U))
#define XRFDC_CTRL_STATS_OFFSET 0x0U
#define XRFDC_HSCOM_ADDR 0x1C00U
#define XRFDC_BLOCK_ADDR_OFFSET(X) (X * 0x400U)
#define XRFDC_TILE_DRP_OFFSET 0x2000U
"""    
    
class BlockDRP(window_array):
    ADC_UPDATE_DYN:    reg(0x1C) # ADC Update Dynamic Register
    DAC_UPDATE_DYN:    reg(0x20)  # DAC Update Dynamic Register
    NCO_FQWD_UPP:      reg(0x94)  # ADC NCO Frequency Word[47:32] Register
    NCO_FQWD_MID:      reg(0x98)  # ADC NCO Frequency Word[31:16] Register
    NCO_FQWD_LOW:      reg(0x9C)  # ADC NCO Frequency Word[15:0] Register
    NCO_UPDT:          reg(0x08C) # ADC/DAC NCO Update mode Register
    NCO_RST:           reg(0x090) # ADC/DAC NCO Phase Reset Register
    NCO_PHASE_UPP:     reg(0x0A0) # ADC/DAC NCO Phase[17:16] Register
    NCO_PHASE_LOW:     reg(0x0A4) # ADC/DAC NCO Phase[15:0] Register
    ADC_NCO_PHASE_MOD: reg(0x0A8) # ADC NCO Phase Mode Register

    def __init__(self):
        super().__init__(0x2000, 0x400, 0x400, 4)
        

class TileWindow(window_array):
    DRP: BlockDRP()

    def __init__(self, offset):
        super().__init__(offset, 0x4000, 0x4000, 4)
    
class RFDC(UIO):
    ADCRegs: TileWindow(0x14000)
    DACRegs: TileWindow(0x04000)
    
    IP_VERSION: reg(0x0000)
    MASTER_RESET: reg(0x0004)
    CISR: reg(0x0008)
    CIER: reg(0x000C)

    XRFDC_TILES_ENABLED_OFFSET: reg(0x00A0) # The tiles enabled in the design
    XRFDC_ADC_PATHS_ENABLED_OFFSET: reg(0x00A4) # The ADC analogue/digital paths enabled in the design
    XRFDC_DAC_PATHS_ENABLED_OFFSET: reg(0x00A8) # The DAC analogue/digital paths enabled in the design */
    #define XRFDC_PATH_ENABLED_TILE_SHIFT 4U /**< A shift to get to the correct tile for the path */


    def __init__(self):
        path = None

        l = list(Path("/sys/bus/platform/devices").glob(f"*.usp_rf_data_converter"))
        assert len(l) == 1, f"Could not determine data converter path: {l}"

        path = l[0]

        super().__init__(path)

        addr = int(self.path.stem, 16)
        
        with open(self.path / "of_node" / "param-list", "rb") as f:
            self.of_param_list = f.read()

        self.params = RFDCConfigParams(self.of_param_list)

        assert addr == self.params.address, "Address from sysfs and param block differ"
        
        self.csr = self.maps[0]

        self.csr.map()

        self.children.ADC = []

        if self.high_speed_ADC:
            self.children.ADC = [ ADCBlock(self, i, j) for i in range(4) for j in [0, 2] ]

        self.children.DAC = [ DACBlock(self, i, j) for i in range(2) for j in range(4) ]
            
    @property
    def high_speed_ADC(self):
        return self.params.ADC[0].slices == 2
        
    @command
    def status(self):
        output.info(f"RFDC IP Version: {self.IP_VERSION}")
        output.info(f"Master Reset: {self.MASTER_RESET}")
        output.info(f"Interrupt Status: {self.CISR}")
        output.info(f"Interrupt Enable: {self.CIER}")
        
    @command
    def reset(self):
        self.MASTER_RESET = 1
