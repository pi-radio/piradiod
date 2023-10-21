from functools import cached_property

import numpy as np

from piradio.util import Freq, Spectrum

class FDSymbol:
    def __init__(self, ofdm, fft=None):
        self.ofdm = ofdm
        if fft is None:
            fft = np.zeros(ofdm.N)
        self.fft = fft

    @property
    def pilots(self):
        return self.fft[self.ofdm.pilot_idxs]

    @pilots.setter
    def pilots(self, v):
        self.fft[self.ofdm.pilot_idxs] = v

    @property
    def data_subcarriers(self):
        return self.fft[self.ofdm.data_idxs]

    @data_subcarriers.setter
    def data_subcarriers(self, v):
        self.fft[self.ofdm.data_idxs] = v

    @property
    def subcarriers(self):
        return self.fft[self.ofdm.subcarrier_idxs]

    @subcarriers.setter
    def subcarriers(self, v):
        self.fft[self.ofdm.subcarrier_idxs] = v
    
    
class CPStrippedSymbol:
    def __init__(self, ofdm, samples):
        self.ofdm = ofdm
        self.samples = samples

        assert len(samples) == self.ofdm.N

    @cached_property
    def fd(self):
        return FDSymbol(self.ofdm, self.samples.spectrum.shifted.fft)
        
    @cached_property
    def spectrum(self):
        return self.samples.spectrum    

class FullSymbol:
    def __init__(self, ofdm, samples):
        self.ofdm = ofdm
        self.samples = samples

        assert len(samples) == self.ofdm.symbol_len, f"Improper symbol length: {len(samples)} != {self.ofdm.symbol_len}"
        
    @property
    def stripped(self):
        pos = self.ofdm.CP_len - self.ofdm.symbol_offset
        return CPStrippedSymbol(self.ofdm, self.samples[pos:pos+self.ofdm.N])


class Frame:
    def __init__(self, ofdm, samples):
        self.ofdm = ofdm
        self.samples = samples

        assert len(samples) == self.ofdm.frame_len
            
    @cached_property
    def symbols(self):
        class Symbols:
            ofdm = self.ofdm
            samples = self.samples

            def __len__(self):
                return len(self.samples) // self.ofdm.symbol_len
            
            def __getitem__(self, i):
                if i >= len(self):
                    raise IndexError()
                
                return FullSymbol(self.ofdm, self.samples[i * self.ofdm.symbol_len:(i+1) * self.ofdm.symbol_len])
            
        return Symbols()

    def plot(self):
        self.samples.plot()
