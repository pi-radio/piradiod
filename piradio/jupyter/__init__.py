import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import pandas as pd
from piradio.util import MHz, GHz, Freq
from piradio.devices import SampleBufferIn, SampleBufferOut, Trigger
from .signals import signals

import IPython
from IPython.core.display import HTML

plt.rcParams['figure.figsize'] = [10, 5]

def restart_kernel():
    display(HTML("<script>Jupyter.notebook.kernel.restart()</script>"))    

def plot_signal(sbuf, **kwargs):
    plot_samples(sbuf.array, **kwargs)

def plot_sample_spectrum(v, sample_rate=1, window=None, xlim=None, ylim=[-130, 0], title=None, min_peak_height=-30, mark_peaks=True):
    if window is None:
        f, ft = sbuf.fft
    else:
        ft = np.fft.fftshift(np.fft.fft(sbuf.array[window[0]:window[1]], mode="forward"))
        f = np.fft.fftshift(np.fft.fftfreq(len(ft), 1/sbi.sample_rate.Hz))
        
    p = np.abs(ft)
    
    p[p == 0] = 1/2**17

    dB = 20 * np.log10(np.abs(p))

    plt.figure()
    plt.plot(f, dB)
    plt.ylim(ylim)

    if xlim is not None:
        plt.xlim(xlim)

    if mark_peaks:
        peaks, props = find_peaks(dB, height=min_peak_height)
        bot = ylim[0]
        top = ylim[1]

        heights = props['peak_heights']

        peak_data = {'Frequency (MHz)': [f[peak]/1e6 for peak in peaks],
                     'Height (dB)': heights}

        df = pd.DataFrame(peak_data)
        #df = df[df["Frequency (Hz)"].between(-0.25e9, 0.25e9)]

        df = df.sort_values("Height (dB)", ascending=False)
        
        plt.vlines(f[peaks], bot, top, color='r')
        
    if title is not None:
        plt.title(title)

    plt.show()
        
def plot_spectrum(sbuf, **kwargs):
    plot_sample_spectrum(sbuf.array, sample_rate=sbuf.sample_rate.Hz, **kwargs)


def recover_fs4(v):
    vp = np.power(np.ones(len(v))*1.0j, -np.mod(np.arange(len(v))+1, 4))

    raw_signal = v * vp

    return v * vp

def real_spectrum(rfin, title=None, min_peak_height=-40):
    ft = np.fft.fftshift(np.fft.fft(rfin, norm="forward"))[len(rfin)//2:]
    freq = np.fft.fftshift(np.fft.fftfreq(len(rfin), 1/4e9))[len(rfin)//2:]
    p = np.abs(ft)
    p[p==0] = 1e-10
    dB = 20 * np.log10(p)

    bot = min(dB)
    top = max(dB)
    
    peaks, props = find_peaks(dB, height=min_peak_height, distance=50)
    
    print(freq[peaks]/1e6)
    print(props["peak_heights"])
    plt.plot(freq,dB)

    if title is not None:
        plt.title(title)
        
    plt.vlines(freq[peaks], bot, top, color='r')
    plt.show()    

def create_ZC_waveform(N, NZC, q, u, interpolation=1):
    n = np.arange(NZC*interpolation)/interpolation
    v = np.zeros(N, dtype=np.cdouble)
    v[0:NZC*interpolation] = np.exp(-1.0j * np.pi * u * n * (n + (NZC & 1) + 2 * q) / NZC)
    return v
    
    
def update_signal_ZC(sbuf, NZC, q, u, interpolation=1):
    sbuf.array = create_ZC_waveform(sbuf.nsamples, NZC, q, u, interpolation)
