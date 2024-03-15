import numpy as np
from functools import cached_property

from scipy.signal import find_peaks, decimate
import pandas as pd
import matplotlib.pyplot as plt
import h5py

from piradio.util import MHz, GHz, Freq, Hz
from .real_spectrum import RealSpectrumFromTimeDomain
from .iq_spectrum import *
    
#def spectrum_from_sample_buffer(SpectrumBase):
#    def __init__(self, sbuf, *args, **kwargs):
#        assert 'sample_rate' not in kwargs
#        
#        return SpectrumFromTimeDomain(sbuf.array, sample_rate=sbuf.sample_rate, **kwargs)

    
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
