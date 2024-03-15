import numpy as np
from functools import cached_property

from scipy.signal import find_peaks, decimate
import pandas as pd
import matplotlib.pyplot as plt
import h5py

from piradio.util import MHz, GHz, Freq, Hz

from .spectrum_base import SpectrumBase

class RealSpectrumBase(SpectrumBase):
    pass

class RealSpectrumFromFFT(RealSpectrumBase):
    def __init__(self, fft, f):
        self._fft = fft
        self._f = f
        self._power = np.real(self.fft * np.conj(self.fft)) / self.N**2

        #print(f"RFFT: {len(fft)} {fft} {len(self._f)} {self._f}")
        
        p = np.copy(self.power)
        p[p == 0] = 1e-10
        self._dB = 10 * np.log10(p)        
        
    @property
    def fft(self):
        return self._fft

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def f(self):
        return self._f

    @property
    def power(self):
        return self._power

    @property
    def dB(self):
        return self._dB


class RealSpectrumFromTimeDomain(RealSpectrumFromFFT):
    def __init__(self, td, decimation=1, sample_rate=Hz(1), window=None):
        if window is None:
            window = [ 0, len(td) ]
            
        td = td[window[0]:window[1]]
            
        if decimation > 1:
            td = decimate(td, decimation)
            sample_rate /= decimation

        self._sample_rate = sample_rate
        self._td = td
            
        f = [ Freq(f) for f in np.fft.rfftfreq(len(td), 1/sample_rate.Hz) ]

        super().__init__(np.fft.rfft(td), f)
            
    
    @property
    def td(self):
        return self._td

    def save(self, name):
        with h5py.File(name, "w") as f:
            grp = f.create_group("spectrum")
            grp['time_domain'] = self.td
            grp['time_domain'].attrs['sample_rate'] = self._sample_rate.hz
            grp['fft'] = self.fft
            grp['f'] = [ f.hz for f in self.f ]

    @classmethod
    def load(self, h5grp):
        sr = Freq(h5grp['time_domain'].attrs['sample_rate'])
        td = h5grp['time_domain'][...]
        fft = h5grp['fft'][...]
        f = [ Freq(f) for f in h5grp['f'][...] ]

        return RealSpectrumFromTimeDomain(td, sample_rate=sr, fft=fft, f=f)
