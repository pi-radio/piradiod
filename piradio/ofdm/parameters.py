import numpy as np

from functools import cached_property

from piradio.util import Freq, Hz, GHz

from .sync_word import SyncWord
from .equalizer import Equalizer
from .modulator import BPSK

class OFDMParameters:

    default_pilot_values = [
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
         1, -1,  1,  1,  1, -1, -1, -1,  1,  1
    ]

    
    def __init__(self,
                 N_fft=1024,
                 sample_rate=GHz(2),
                 pilot_values=default_pilot_values,
                 pilot_spacing=4
                 ):
        self.sample_rate = sample_rate
        self.N_fft = N_fft
        self.pilot_values = pilot_values
        self.pilot_spacing = pilot_spacing
        self.LO_space = 2
        self.N_guard_band = (self.N_fft - self.subcarriers) // 2
        self.symbol_offset = 10

        self.lo_guard_idxs = np.arange(self.LO_space) + self.N_guard_band + self.subcarriers // 2
        self.guard_band_idxs = np.concatenate((np.arange(self.N_guard_band), self.lo_guard_idxs, np.arange(self.N_guard_band) + 4096 - self.N_guard_band ))
        
        self.subcarrier_idxs = np.delete(np.arange(self.N), self.guard_band_idxs)

        self.pilot_idxs = np.concatenate((self.subcarrier_idxs[:self.data_subcarriers//2:self.pilot_spacing],
                                          self.subcarrier_idxs[-self.data_subcarriers//2::self.pilot_spacing]))
        

        self.data_idxs = self.subcarrier_idxs[np.where(np.isin(self.subcarrier_idxs, self.pilot_idxs) == False)]
        
    @property
    def N(self):
        return self.N_fft
        
    @property
    def SCS(self):
        return self.sample_rate/self.N_fft

    @property
    def BW(self):
        return (self.subcarriers + 2) * self.SCS

    @property
    def npilots(self):
        return len(self.pilot_values)
        
    
    @property
    def CP_len(self):
        return self.N_fft // 4

    @property
    def frame_symbols(self):
        return 1
    
    @property
    def data_subcarriers(self):
        return self.pilot_spacing * self.npilots

    @property
    def subcarriers(self):
        return self.data_subcarriers + self.LO_space

    
    @property
    def symbol_len(self):
        return self.N_fft + self.CP_len

    @property
    def frame_len(self):
        return (self.frame_symbols + 1) * self.symbol_len
    
    @cached_property
    def BPSK(self):
        return BPSK(self)
    
    @cached_property
    def sync_word(self):
        return SyncWord(self)

    @cached_property
    def equalizer(self):
        return Equalizer(self)
    
    def extract_subcarriers(self, samples):
        fft = np.fft.fftshift(samples.spectrum.fft)
        assert len(fft) == self.N_fft

        return fft[self.subcarrier_idxs]
    
    def extract_pilots(self, subcarriers):
        return np.concatenate((subcarriers[0:self.data_subcarriers//2:self.pilot_spacing],
                               subcarriers[-self.data_subcarriers//2::self.pilot_spacing]))
