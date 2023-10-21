import numpy as np
from scipy.signal import find_peaks, decimate
import pandas as pd
import matplotlib.pyplot as plt

from piradio.util import MHz, GHz, Freq
from piradio.devices import SampleBufferIn, SampleBufferOut

class Spectrum:
    class _shifter:
        def __init__(self, spec):
            self.spec = spec

        def __getattr__(self, attr):
            if attr in [ "f", "f_Hz", "power", "dB", "fft" ]:
                return np.fft.fftshift(getattr(self.spec, attr))
            raise AttributeError(attr)

    def __init__(self, v, decimation=1, sample_rate=None, shift=True, window=None):
        if hasattr(v, "is_sample_buffer"):
            if sample_rate is None:
                sample_rate = v.sample_rate
            v = v.array

        if decimation > 1:
            v = decimate(v, decimation)
            
            if sample_rate is not None:
                sample_rate /= decimation

        if window is not None:
            v = v[window[0]:window[1]]

        self.td = v
        self.fft = np.fft.fft(v)

        self.f = np.fft.fftfreq(len(self.fft), 1.0)
        
        if sample_rate is not None:
            self.f = np.array(list(map(lambda x: x * sample_rate, self.f)))

        self.shifted = self._shifter(self)

    @property
    def f_Hz(self):
        return np.array(list(map(lambda x: x.Hz, self.f)))

    @property
    def N(self):
        return len(self.f)
    
    @property
    def power(self):
        return np.real(self.fft * np.conj(self.fft)) / self.N**2

    @property
    def dB(self):
        p = self.power
        p[p == 0] = 1/2**17
        return 10 * np.log10(p)
    
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
        
