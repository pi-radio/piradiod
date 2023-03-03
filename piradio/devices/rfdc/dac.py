from piradio.devices.uio import UIO
from piradio.command import CommandObject, cmdproperty
from piradio.util import Freq, GHz, MHz

class DACBlock(CommandObject):
    EVENT_SOURCE_IMMEDIATE = 0

    UPDATE_EVENT_MASK = 0xF

    UPDATE_EVENT_SLICE = 0x1
    UPDATE_EVENT_NCO = 0x2
    UPDATE_EVENT_QMC = 0x4
    UPDATE_EVENT_COARSE_DELAY = 0x8 # differs for DAC
    
    NCO_UPDATE_MODE_MASK = 0x7

    NCO_DIV = 1 << 48
    
    def __init__(self, rfdc, tile, block):
        self.rfdc = rfdc
        self.tile = tile
        self.block = block

    @property
    def DRP(self):
        return self.rfdc.DACRegs[self.tile].DRP[self.block]

    @property
    def sampling_rate(self):
        return GHz(self.rfdc.params.DAC[self.tile].sampling_rate)
    
    @cmdproperty
    def nco_freq(self):
        upp = self.DRP.NCO_FQWD_UPP
        mid = self.DRP.NCO_FQWD_MID
        low = self.DRP.NCO_FQWD_LOW

        v = ((upp << 32) | (mid << 16) | low) / self.NCO_DIV

        return self.sampling_rate * v

    @nco_freq.setter
    def nco_freq(self, f : Freq):
        assert f < self.sampling_rate
        assert f >= MHz(0.0)

        v = int(f * self.NCO_DIV / self.sampling_rate)

        self.DRP.NCO_FQWD_LOW = v & 0xFFFF
        self.DRP.NCO_FQWD_MID = (v >> 16) & 0xFFFF
        self.DRP.NCO_FQWD_UPP = (v >> 32) & 0xFFFF

        self.DRP.NCO_UPDT = (self.DRP.NCO_UPDT & ~self.NCO_UPDATE_MODE_MASK) | self.EVENT_SOURCE_IMMEDIATE
        self.DRP.ADC_UPDATE_DYN |= self.UPDATE_EVENT_NCO

