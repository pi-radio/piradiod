import numpy as np
from functools import cached_property

from scipy.signal import find_peaks, decimate
import pandas as pd
import matplotlib.pyplot as plt
import h5py

from piradio.util import MHz, GHz, Freq, Hz

class SpectrumBase:
    """
    Subclass properties:
     - f: frequency bins
     - fft: signal based fft
     - dB: logarithmic magnitude fft (power)
     - power: linear power
    """
    class _shifter:
        def __init__(self, spec):
            self.spec = spec

        def __getattr__(self, attr):
            if attr in [ "f", "f_Hz", "power", "dB", "fft" ]:
                return np.fft.fftshift(getattr(self.spec, attr))
            raise AttributeError(attr)

    @cached_property
    def shifted(self):
        return SpectrumBase._shifter(self)
        
    @property
    def f_Hz(self):
        return np.array(list(map(lambda x: x.Hz, self.f)))

    @property
    def N(self):
        return len(self.f)


    @property
    def LO_dB(self):
        return self.dB[len(self.freq)//2]

    @property
    def LO_power(self):
        return self.power[len(self.freq)//2]    
    
    @property
    def bin_width(self):
        return self.f[1] - self.f[0]
        
    def freq_bin(self, f):
        return np.argmin([ np.abs(bf - f) for bf in self.f ] )

        
    def find_signal(self, f, w=1):
        def find_one(f, w=1):
            b = self.freq_bin(f)
        
            return b - w + np.argmax(self.power[b-w:b+w+1])

        try:
            fiter = iter(f)
        except TypeError:
            return find_one(f, w)

        return np.array([ find_one(f) for f in fiter ])


    def SINAD(self, f, w=1, bw=None):
        ps = np.sum(self.power[self.find_signal(f, w)])

        if bw is None:
            s = np.sum(self.power[1:])
        else:
            o = round(bw / 2 / self.f[1])
            s = np.sum(self.power[1:o]) + np.sum(self.power[-o:])

        s -= ps + self.LO_power
        
        return 10 * np.log10(ps / s)

    def SFDR(self, f, w=1):
        idxs = self.find_signal(f, w)

        try:
            n = len(idxs)
        except:
            n = 1

        p = np.copy(self.power)

        sp = np.sum(self.power[idxs]) / n

        p[idxs] = 0
        p[self.N//2] = 0
        
        return 10 * np.log10(self.power[b] / np.max[p])
    
    def plot(self, xlim=None, ylim=[-130, 0], title=None, min_peak_height=-30, mark_peaks=True):
        m = max(self.f)

        div, label = m.friendly_tuple

        plt.figure()
        plt.plot(self.shifted.f_Hz/div, self.shifted.dB)
        plt.xlabel(label)
        plt.ylim(ylim)

        if xlim is not None:
            plt.xlim(xlim)

        if mark_peaks:
            peaks, props = find_peaks(self.shifted.dB, height=min_peak_height)
            bot = ylim[0]
            top = ylim[1]

            heights = props['peak_heights']

            peak_data = {'Frequency (MHz)': [self.shifted.f[peak].MHz for peak in peaks],
                         'Height (dB)': heights}

            df = pd.DataFrame(peak_data)
            #df = df[df["Frequency (Hz)"].between(-0.25e9, 0.25e9)]

            df = df.sort_values("Height (dB)", ascending=False)

            display(df)
        
            plt.vlines(self.shifted.f_Hz[peaks]/div, bot, top, color='r')
        
        if title is not None:
            plt.title(title)

        plt.show()

    def plot_IQ(self, xlim=[-1.5,1.5], ylim=[-1.5, 1.5], title=None):
        plt.figure()
        plt.scatter(np.real(self.fft), np.imag(self.fft))
        plt.xlim(xlim)
        plt.ylim(ylim)
        if title is not None:
            plt.title(title)
        plt.show()
