import numpy as np
from scipy.signal import find_peaks, decimate
import pandas as pd
import matplotlib.pyplot as plt
import json


from piradio.util import MHz, GHz, Freq
from piradio.devices import SampleBufferIn, SampleBufferOut

from .spectrum import Spectrum

class Samples:
    def __init__(self, samples, sample_rate=1, decimation=1):
        if hasattr(samples, "is_sample_buffer"):
            sample_rate = samples.sample_rate
            samples = samples.array
            
        if not hasattr(sample_rate, "hz"):
            sample_rate = Freq(sample_rate)
        
        self.samples = samples
        self.sample_rate = sample_rate

        if decimation != 1:
            self.samples = decimate(self.samples, decimation)
            self.sample_rate /= decimation

    @property
    def t(self):
        return np.arange(len(self.samples), dtype=np.double)/self.sample_rate.hz

    @property
    def duration(self):
        return (len(self.samples) - 1)/self.sample_rate.hz
    
    @property
    def spectrum(self):
        return Spectrum(self.samples, sample_rate=self.sample_rate)

    @property
    def mean(self):
        return np.mean(self.samples)

    def save(self, name : str):
        serdict = {
            'sample_rate' : self.sample_rate.hz,
            'samples' : [ { 'r': np.real(s), 'i': np.imag(s) } for s in self.samples ]
        }

        with open(name, "w") as f:
            json.dump(serdict, f)

    @classmethod
    def load(cls, name : str):
        with open(name, "r") as f:
            d = json.load(f)

        return Samples(sample_rate = Freq(d['sample_rate']),
                       samples = [ v['r'] + 1.0j * v['i'] for v in d['samples'] ])
                                   
            
    @property
    def std(self):
        return np.std(self.samples)

    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, k):
        if isinstance(k, slice):
            sr = self.sample_rate
            if k.step is not None:
                sr /= k.step
                
            return Samples(self.samples[k], sr)

        
        v = self.samples[k]

        if hasattr(v, "__len__"):
            return Samples(v, 0)

        return v
    
    def plot(self, xlim=None, ylim=[-1,1]):
        plt.figure()
        plt.plot(self.t, np.real(self.samples))
        plt.plot(self.t, np.imag(self.samples))
        if xlim is not None:
            plt.xlim(xlim)
        plt.ylim(ylim)
        plt.show()

    def conjugate(self):
        return Samples(np.conjugate(self.samples), self.sample_rate)

    def decimate(self, n=2):
        return Samples(decimate(self.samples, n), self.sample_rate/2)
        
    @property
    def fs4(self):
        return Samples(self.samples * np.tile([1, -1j, -1, 1j], len(self.samples)//4), self.sample_rate)
        
            
