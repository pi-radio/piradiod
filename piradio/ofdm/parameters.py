import numpy as np

from functools import cached_property

from piradio.util import Freq, Hz, MHz, GHz

from .sync_word import OFDM1SyncWord, IEEE20SyncWord
from .synchronizer import Synchronizer
from .equalizer import Equalizer
from .modulator import BPSK
from .symbol import Frame, FullSymbol

class OFDMParameters:
    frame_symbols = 1
    symbol_offset = 0
    
    def __init__(self):
        if not hasattr(self, "Ncp"):
            self.Ncp = self.N // 4
    
    @property
    def SCS(self):
        return self.sample_rate/self.N_fft

    @property
    def BW(self):
        return (self.subcarriers + 2) * self.SCS

    @property
    def symbol_len(self):
        return self.N + self.Ncp    

    @property
    def frame_len(self):
        return (self.frame_symbols + 1) * self.symbol_len

    @property
    def frame_time(self):
        return self.frame_len / self.sample_rate
    
    @property
    def NDSC(self):
        return len(self.data_idxs)

    @cached_property
    def subcarrier_idxs(self):
        return np.sort(np.concatenate((self.pilot_idxs, self.data_idxs)))
    
    @cached_property
    def BPSK(self):
        return BPSK(self)
    
    @cached_property
    def sync_word(self):
        return self.sync_word_class(self)

    @cached_property
    def synchronizer(self):
        return Synchronizer(self)

    @cached_property
    def equalizer(self):
        return Equalizer(self)

    def frame(self, samples):
        return Frame(self, samples)
    
    def full_symbol(self, samples):
        return FullSymbol(self, samples)

class OFDMGeorge(OFDMParameters):
    george_pilot_values = [
         1, -1,  1,  1, -1,  1, -1,  1, -1,  1,
        -1,  1,  1,  1, -1,  1,  1,  1, -1, -1,
         1, -1,  1, -1,  1, -1, -1, -1,  1,  1,
        -1,  1,  1, -1, -1, -1,  1, -1,  1,  1,
        -1, -1,  1,  1,  1, -1, -1,  1, -1,  1,
         1, -1,  1, -1,  1,  1, -1, -1,  1,  1,
         1,  1,  1, -1, -1,  1, -1,  1, -1, -1,
         1,  1, -1, -1, -1,  1, -1, -1, -1, -1,
         1, -1, -1, -1,  1, -1, -1, -1, -1,  1,
         1, -1,  1, -1,  1,  1, -1, -1, -1, -1,
        
         1,  1, -1,  1,  1,  1,  1,  1, -1,  1,
         1, -1, -1,  1, -1,  1, -1, -1,  1, -1,
        -1, -1,  1,  1,  1,  1, -1, -1,  1,  1,
        -1,  1,  1,  1,  1,  1, -1,  1, -1, -1,
        -1,  1, -1, -1, -1,  1, -1, -1,  1, -1,
         1,  1,  1,  1, -1,  1,  1,  1,  1, -1,
         1,  1, -1, -1,  1,  1, -1,  1, -1,  1,
        -1, -1,  1, -1, -1,  1,  1,  1,  1,  1,
        -1, -1,  1,  1,  1, -1, -1, -1,  1, -1,
         1, -1,  1,  1,  1, -1, -1, -1,  1,  1,
    ]
    

class OFDMStructure1(OFDMParameters):
    N = 1024
    LO_space = 2
    
    pilot_values = [
         1, -1,  1,  1, -1,  1, -1,  1, -1,  1,
        -1,  1,  1,  1, -1,  1,  1,  1, -1, -1,
         1, -1,  1, -1,  1, -1, -1, -1,  1,  1,
        -1,  1,  1, -1, -1, -1,  1, -1,  1,  1,
        -1, -1,  1,  1,  1, -1, -1,  1, -1,  1,
         1, -1,  1, -1,  1,  1, -1, -1,  1,  1,
         1,  1,  1, -1, -1,  1, -1,  1, -1, -1,
         1,  1, -1, -1, -1,  1, -1, -1, -1, -1,
         1, -1, -1, -1,  1, -1, -1, -1, -1,  1,
         1, -1,  1, -1,  1,  1, -1, -1, -1, -1,  1,
        
         1,  1, -1,  1,  1,  1,  1,  1, -1,  1,
         1, -1, -1,  1, -1,  1, -1, -1,  1, -1,
        -1, -1,  1,  1,  1,  1, -1, -1,  1,  1,
        -1,  1,  1,  1,  1,  1, -1,  1, -1, -1,
        -1,  1, -1, -1, -1,  1, -1, -1,  1, -1,
         1,  1,  1,  1, -1,  1,  1,  1,  1, -1,
         1,  1, -1, -1,  1,  1, -1,  1, -1,  1,
        -1, -1,  1, -1, -1,  1,  1,  1,  1,  1,
        -1, -1,  1,  1,  1, -1, -1, -1,  1, -1,
         1, -1,  1,  1,  1, -1, -1, -1,  1,  1, -1
    ]

    sync_word_class=OFDM1SyncWord
    
    npilots = len(pilot_values)
    pilot_spacing = 4
    
    half_width_sc =  (npilots // 2 - 1) * pilot_spacing + 1

    loff = ((N - LO_space) // 2) - half_width_sc
    roff = N // 2 + LO_space // 2

    half_sc_i = np.arange(half_width_sc)

    half_pilot_sc_i = np.arange(npilots//2) * pilot_spacing

    half_data_sc_i = np.delete(half_sc_i, half_pilot_sc_i)

    pilot_idxs = np.concatenate((half_pilot_sc_i + loff,
                                 half_pilot_sc_i + roff))
        
    data_idxs = np.concatenate((half_data_sc_i + loff,
                                half_data_sc_i + roff))
    
    subcarrier_idxs = np.sort(np.concatenate((pilot_idxs, data_idxs)))
        
    zero_idxs = np.delete(np.arange(N), subcarrier_idxs)

    
    

class IEEE_802_11_20MHz(OFDMParameters):
    N = 64

    sync_word_class = IEEE20SyncWord
    
    sample_rate = MHz(40)

    pilot_idxs = 32 + np.array([ -21, -7, 7, 21 ])

    pilot_values = [ 1, -1, -1, 1 ]
    
    data_idxs = np.concatenate((32 + np.arange(26) - 26, 32 + 1 + np.arange(26)))
    data_idxs = np.delete(data_idxs, np.where(np.isin(data_idxs, pilot_idxs)))

    
class OFDM2(OFDMParameters):
    N = 64

    sync_word_class = IEEE20SyncWord
    
    sample_rate = MHz(160)

    pilot_idxs = 32 + np.array([ -21, -7, 7, 21 ])

    pilot_values = [ 1, -1, -1, 1 ]
    
    data_idxs = np.concatenate((32 + np.arange(26) - 26, 32 + 1 + np.arange(26)))
    data_idxs = np.delete(data_idxs, np.where(np.isin(data_idxs, pilot_idxs)))
                            
class OFDM_DOCSIS_1(OFDMParameters):
    N = 8192

    
