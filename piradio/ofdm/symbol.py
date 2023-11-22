from functools import cached_property

import numpy as np
import matplotlib.pyplot as plt

from piradio.util import Freq, Spectrum, Samples
from piradio.util.spectrum import SpectrumFromFFT

class FDSymbol:
    def __init__(self, ofdm, fft=None, stripped=None):
        self.ofdm = ofdm
        if fft is None:
            fft = np.zeros(ofdm.N, dtype=np.cdouble)
        self._fft = fft
        self._stripped = stripped

    @property
    def fft(self):
        return np.fft.ifftshift(self._fft)
        
    @property
    def pilots(self):
        return self._fft[self.ofdm.pilot_idxs]

    @pilots.setter
    def pilots(self, v):
        self._fft[self.ofdm.pilot_idxs] = v

    @property
    def data_subcarriers(self):
        return self._fft[self.ofdm.data_idxs]

    @data_subcarriers.setter
    def data_subcarriers(self, v):
        self._fft[self.ofdm.data_idxs] = v

    @property
    def subcarriers(self):
        return self._fft[self.ofdm.subcarrier_idxs]

    @subcarriers.setter
    def subcarriers(self, v):
        self._fft[self.ofdm.subcarrier_idxs] = v

    @property
    def stripped(self):
        if self._stripped is None:
            s = np.fft.ifft(self.fft)
            
            self._stripped = CPStrippedSymbol(self.ofdm,
                                              samples=Samples(np.fft.ifft(self.fft), sample_rate=self.ofdm.sample_rate),
                                              fd=self)

        return self._stripped

    @property
    def full(self):
        return self.stripped.full

    @property
    def td(self):
        return self.full
    
    def plot(self, *args, **kwargs):
        SpectrumFromFFT(self.fft, sample_rate = self.ofdm.sample_rate).plot(*args, **kwargs)

    def plot_IQ(self, *args, **kwargs):
        SpectrumFromFFT(self.fft, sample_rate = self.ofdm.sample_rate).plot_IQ(*args, **kwargs)

        
class CPStrippedSymbol:
    def __init__(self, ofdm, samples, fd=None, full=None):
        self.ofdm = ofdm
        self.samples = samples
        self._fd = fd
        self._full = full

        assert len(samples) == self.ofdm.N

    @property
    def fd(self):
        if self._fd is None:
            self._fd = FDSymbol(self.ofdm, self.samples.spectrum.shifted.fft, stripped=self)

        return self._fd
            
    @cached_property
    def spectrum(self):
        return self.samples.spectrum

    @property
    def full(self):
        if self._full is None:
            self._full = FullSymbol(self.ofdm, Samples.concatenate(self.samples[-self.ofdm.CP_len:], self.samples), stripped=self)
        return self._full

    def plot(self, *args, **kwargs):
        self.samples.plot(*args, **kwargs)
    
class FullSymbol:
    def __init__(self, ofdm, samples, stripped=None):
        self.ofdm = ofdm
        self.samples = samples
        self._stripped = stripped

        assert len(samples) == self.ofdm.symbol_len, f"Improper symbol length: {len(samples)} != {self.ofdm.symbol_len}"

    def __getitem__(self, v):
        return self.samples[v]

    @property
    def cfo_est(self):
        phi = -np.angle(np.sum(np.conj(self.samples[:self.ofdm.CP_len]) * self.samples[-self.ofdm.CP_len:]))

        return phi / self.ofdm.N

    @property
    def cfo_est_freq(self):
        return self.cfo_est * self.ofdm.sample_rate / 2 / np.pi
    
    def eq_cfo(self):
        self._stripped = None
        self.samples = self.samples * np.exp(1.0j * self.cfo_est * np.arange(len(self.samples)))
        
    @property
    def stripped(self):
        if self._stripped is None:
            pos = self.ofdm.CP_len - self.ofdm.symbol_offset
            self._stripped = CPStrippedSymbol(self.ofdm, self.samples[pos:pos+self.ofdm.N], full=self)

        return self._stripped

    @property
    def fd(self):
        return self.stripped.fd

    def plot(self, *args, **kwargs):
        self.samples.plot(*args, **kwargs)
    

class Frame:
    def __init__(self, ofdm, samples):
        assert len(samples) == ofdm.frame_len

        self.ofdm = ofdm
        self.symbols = tuple(FullSymbol(self.ofdm, samples[i * self.ofdm.symbol_len:(i+1) * self.ofdm.symbol_len]) for i in range(ofdm.frame_symbols+1))

            
    def plot(self, *args, **kwargs):
        Samples.concatenate(*[ s.samples for s in self.symbols ]).plot(*args, **kwargs)
