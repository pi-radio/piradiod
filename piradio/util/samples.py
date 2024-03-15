import numpy as np
from scipy.signal import find_peaks, decimate, resample
import pandas as pd
import matplotlib.pyplot as plt
import json
import h5py

from piradio.util import MHz, GHz, Freq

from .spectrum import Spectrum, RealSpectrum

REAL_SAMPLES=0
IQ_SAMPLES=1

class Samples:
    def __init__(self, samples, sample_rate=1, decimation=1, real=False):
        if hasattr(samples, "is_sample_buffer"):
            sample_rate = samples.sample_rate
            real = True if samples.sample_format == REAL_SAMPLES else False
            samples = samples.array
            
        if not hasattr(sample_rate, "hz"):
            sample_rate = Freq(sample_rate)

        self.real = real
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
        return (len(self.samples)-1)/self.sample_rate.hz
    
    @property
    def spectrum(self):
        if self.real:
            return RealSpectrum(self.samples, sample_rate=self.sample_rate)
        else:
            return Spectrum(self.samples, sample_rate=self.sample_rate)

    @property
    def mean(self):
        return np.mean(self.samples)

    @property
    def mean_power(self):
        return self.total_power / len(self)

    @property
    def total_power(self):
        return np.real(np.sum(self.samples * np.conjugate(self.samples)))
    
    def save(self, name : str):
        with h5py.File(name, "w") as f:
            f['samples'] = self.samples
            f['samples'].attrs['sample_rate'] = self.sample_rate.hz

    @classmethod
    def load(cls, name : str):
        with h5py.File(name, "r") as f:
            return Samples(sample_rate = Freq(f['samples'].attrs['sample_rate']),
                           samples = f['samples'][...])
                                   
            
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
    
    def plot(self, xlim=None, ylim=[-1,1], fit=False):
        plt.figure()
        plt.plot(self.t, np.real(self.samples))
        
        if not self.real:
            plt.plot(self.t, np.imag(self.samples))
            
        if xlim is not None:
            plt.xlim(xlim)

        if fit:
            m = 1.25 * max(max(np.real(self.samples)), max(np.imag(self.samples)))
            ylim = [ -m, m ]
            
        plt.ylim(ylim)
        plt.show()

    def plot_IQ(self, xlim=[-1,1], ylim=[-1, 1], title=None):
        assert not self.real
        
        plt.figure()
        plt.scatter(np.real(self.samples), np.imag(self.samples), s=1)

        if xlim == "auto":
            mean = np.mean(np.real(self.samples))
            rmin = np.min(np.real(self.samples))
            rmax = np.max(np.real(self.samples))
            xlim = [ mean + (rmin - mean) * 1.5, mean + (rmax-mean) * 1.5 ]

        if ylim == "auto":
            mean = np.mean(np.imag(self.samples))
            imin = np.min(np.imag(self.samples))
            imax = np.max(np.imag(self.samples))
            ylim = [ mean + (imin - mean) * 1.5, mean + (imax-mean) * 1.5 ]

            
        plt.xlim(xlim)
        plt.ylim(ylim)
        if title is not None:
            plt.title(title)
        plt.show()

    def eye_diagram(self, period):
        x = self.t % period

        plt.scatter(x, np.real(self.samples), s=1)
        plt.show()
        
        plt.scatter(x, np.imag(self.samples), s=1)
        plt.show()
        
    def conjugate(self):
        return Samples(np.conjugate(self.samples), self.sample_rate)

    def decimate(self, n=2):
        return Samples(decimate(self.samples, n), self.sample_rate/n)

    def resample(self, N=None, sample_rate=None):
        assert N is not None or sample_rate is not None
        assert not (N is not None and sample_rate is not None)

        samples = self.samples
        
        if N is None:
            frac = sample_rate / self.sample_rate            
            N = int(len(samples) * frac)            
            Nsrc = int(N / frac)
            samples = samples[:Nsrc]

        new_rate = self.sample_rate * N / len(samples)
                        
        return Samples(resample(samples, N), new_rate)

    def __mul__(self, o):
        if isinstance(o, (int, float)):
            return Samples(o * self.samples, sample_rate=self.sample_rate)

        if isinstance(o, np.ndarray):
            return Samples(self.samples * o, sample_rate = self.sample_rate)
        
        raise RuntimeError(f"Unable to multiply samples by {type(o)}")

    def __rmul__(self, o):
        if isinstance(o, (int, float)):
            return Samples(o * self.samples, sample_rate=self.sample_rate)
        raise RuntimeError(f"Unable to multiply samples by {type(o)}")
    
    @property
    def fs4(self):
        return Samples(self.samples * np.tile([1, -1j, -1, 1j], len(self.samples)//4), self.sample_rate)

    @classmethod
    def concatenate(cls, *args):
        for a in args:
            assert a.sample_rate == args[0].sample_rate

        return Samples(np.concatenate([ a.samples for a in args ]), sample_rate=args[0].sample_rate)

    @classmethod
    def zeros(cls, N, *args, **kwargs):
        return Samples(np.zeros(N), *args, **kwargs)
    
    
def lanczos_interpolate(v, n, a):
    """
    n - interpolation order
    a - input sample window width
    """
    
    def lanczos(x, a):
        return np.sinc(x)*np.sinc(x/a) if abs(x) <= a else 0
    
    l = np.vectorize(lanczos)
    
    ix = np.array([ [ i / n ] * (2*a+1) for i in range(n) ])

    print(ix)
    
    sidx = np.tile(np.arange(2*a+1)-a, (n, 1))
    
    print(sidx)
    
    sidx = sidx + ix
    k = l(sidx, a)
    v = np.concatenate((v[-a:], v, v[:a]))
    v = np.array([ np.convolve(v, row, mode="valid") for row in k ]).flatten(order='F')
        
    plt.plot(v)
    
    return v
