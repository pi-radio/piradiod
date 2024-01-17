import numpy as np
from functools import cached_property

from scipy.signal import find_peaks, decimate
import pandas as pd
import matplotlib.pyplot as plt
import h5py

from piradio.util import MHz, GHz, Freq, Hz
from .spectrum_base import SpectrumBase
            
class SpectrumFrom_dB_Power(SpectrumBase):
    def __init__(self, freqs, dB):
        self._dB = dB
        self._f = [ Hz(f) for f in freqs ]

        self._power = 10**(self._dB/10)

    @property
    def shifted(self):
        return self
        
    @property
    def f(self):
        return self._f
        
    @property
    def dB(self):
        return self._dB

    @property
    def power(self):
        return self._power

    def save(self, name):
        with h5py.File(name, "w") as f:
            grp = f.create_group("spectrum")
            grp['dB'] = self.dB
            grp['f'] = [ f.hz for f in self.f ]

    @classmethod
    def load(self, h5grp):
        f = [ Freq(f) for f in h5grp['f'][...] ]
        dB = h5grp['dB'][...]
        
        return SpectrumFrom_dB_Power(f, dB)
            
class SpectrumFromFFT(SpectrumBase):
    def __init__(self, fft, f=None, sample_rate=Hz(1), shifted=False):
        if shifted:
            self._fft = np.fft.ifftshift(fft)
        else:
            self._fft = fft
        self._sample_rate = sample_rate
        self._f = [ Freq(f) for f in np.fft.fftfreq(len(self._fft), 1/sample_rate.Hz) ]
        self._power = np.real(self.fft * np.conj(self.fft)) / self.N**2

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
    
    
class SpectrumFromTimeDomain(SpectrumFromFFT):
    def __init__(self, td, fft=None, f=None, decimation=1, sample_rate=Hz(1), window=None):
        if window is None:
            window = [ 0, len(td) ]
            
        td = td[window[0]:window[1]]
            
        if decimation > 1:
            td = decimate(td, decimation)
            sample_rate /= decimation

        self._td = td

        if fft is None:
            fft = np.fft.fft(td)

        if f is None:
            f = np.fft.fftfreq(len(fft), 1) * sample_rate

        super().__init__(fft, f=f, sample_rate=sample_rate)
            
    
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

        return SpectrumFromTimeDomain(td, sample_rate=sr, fft=fft, f=f)
        
    

    
def spectrum_from_sample_buffer(SpectrumBase):
    def __init__(self, sbuf, *args, **kwargs):
        assert 'sample_rate' not in kwargs
        
        return SpectrumFromTimeDomain(sbuf.array, sample_rate=sbuf.sample_rate, **kwargs)

from .real_spectrum import RealSpectrumFromTimeDomain
    
def RealSpectrum(v, **kwargs):
    return RealSpectrumFromTimeDomain(v, **kwargs)
    
    
def Spectrum(v, **kwargs):
    if hasattr(v, "is_sample_buffer"):
        return spectrum_from_sample_buffer(v, **kwargs)

    return SpectrumFromTimeDomain(v, **kwargs)

def load_spectrum(name):
    with h5py.File(name, "r") as f:
        spec = f["spectrum"]

        if "time_domain" in spec:
            return SpectrumFromTimeDomain.load(spec)
        if "dB" in spec:
            return SpectrumFrom_dB_Power.load(spec)
        
Spectrum.load = load_spectrum
