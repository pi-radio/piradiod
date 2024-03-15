import numpy as np
from functools import cached_property

from scipy.signal import find_peaks, decimate
import pandas as pd
import matplotlib.pyplot as plt
import h5py

from piradio.util import MHz, GHz, Freq, Hz

class SpectrumBase:
        
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
        
    def find_signal(self, f, w=1):
        def find_one(f, w=1):
            b = np.argmin([ np.abs(bf - f) for bf in self.f ] )

            fa = self.f[b-w:b+w+1]
            pa = self.dB[b-w:b+w+1]

            i = np.argmax(pa)
            
            return (fa[i], pa[i])

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

    @property
    def plot_x_vals(self):
        return self.f_Hz

    @property
    def plot_y_vals(self):
        return self.dB

    
    def plot(self, xlim=None, ylim=[-130, 0], title=None, min_peak_height=-30, mark_peaks=True):
        m = max(self.f)

        div, label = m.friendly_tuple

        plt.figure()
        plt.plot(self.plot_x_vals, self.plot_y_vals)
        plt.xlabel(label)
        plt.ylim(ylim)

        if xlim is not None:
            plt.xlim(xlim)

        if mark_peaks:
            peaks, props = find_peaks(self.plot_y_vals, height=min_peak_height)
            bot = ylim[0]
            top = ylim[1]

            heights = props['peak_heights']

            peak_data = {'Frequency (MHz)': [self.plot_x_vals[peak] / 1e6 for peak in peaks],
                         'Height (dB)': heights}

            df = pd.DataFrame(peak_data)
            #df = df[df["Frequency (Hz)"].between(-0.25e9, 0.25e9)]

            df = df.sort_values("Height (dB)", ascending=False)

            display(df)
        
            plt.vlines(self.plot_x_vals[peaks]/div, bot, top, color='r')
        
        if title is not None:
            plt.title(title)

        plt.show()
