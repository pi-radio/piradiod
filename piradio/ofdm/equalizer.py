import numpy as np
from scipy.interpolate import interp1d

import matplotlib.pyplot as plt

from piradio.util import Samples, Freq

from .symbol import FullSymbol, FDSymbol

def plot_IQ(samp, title=None, xlim=[-2,2], ylim=[-2, 2]):
    if title is not None:
        plt.suptitle(title, fontsize="x-large")

    if xlim is not None:
        plt.xlim(xlim)

    if ylim is not None:
        plt.ylim(ylim)
        
    plt.scatter(np.real(samp), np.imag(samp))
    plt.show()

class Equalizer:
    def __init__(self, ofdm):
        self.ofdm = ofdm

    def window_estimate_cfo(self, samples):
        A = samples[:-self.ofdm.N]
        B = samples[self.ofdm.N:]
        
        A2 = np.real(A * np.conj(A))
        B2 = np.real(B * np.conj(B))
    
        C = A * np.conj(B)
        D = (A2 + B2) / 2
    
        gamma = np.convolve(np.ones(self.ofdm.CP_len), C, mode="valid")
        phi = np.convolve(np.ones(self.ofdm.CP_len), D, mode="valid")
        rho = snr_est/(snr_est+1)
        l = np.abs(phi) - rho * gamma
        
        arg_gamma = -np.angle(gamma) / 2 / np.pi
        
        theta_ml = np.argmax(l)
        epsilon_ml = arg_gamma[theta_ml]
        
        f_ml = epsilon_ml * ofdm.SCS.hz
        
        print(f"CFO offset estimate: {f_ml}")
        
        plt.plot(arg_gamma  * ofdm.SCS.hz)
        plt.plot(l/np.max(l) * ofdm.SCS.hz * np.max(np.abs(arg_gamma)) )
        plt.show()
        
        return f_ml          

    def eq_zf(self, symbols):
        ofdm = self.ofdm

        
        def H(d1, d2):
            return d1 * np.conjugate(d2) / np.real(d2 * np.conjugate(d2))

        def zf(rx, pilots):
            Hpilots = H(rx.pilots, pilots)

            # Interpolate magnitude and angle
            mag = interp1d(ofdm.pilot_idxs, np.abs(Hpilots),
                           fill_value="extrapolate")(ofdm.data_idxs)
            
            angle = interp1d(ofdm.pilot_idxs, np.unwrap(np.angle(Hpilots)),
                             fill_value="extrapolate")(ofdm.data_idxs)

            Hdata = mag * np.exp(1.0j * angle)

            outsym = FDSymbol(ofdm)

            outsym.pilots = rx.pilots / Hpilots
            outsym.data_subcarriers = rx.data_subcarriers / Hdata

            return outsym
            
        
        rxsw = symbols[0]
        txsw = ofdm.sync_word

        Hsw = H(rxsw.fd.subcarriers, txsw.fd.subcarriers)

        sw_mag = np.abs(Hsw)
        sw_angle = np.unwrap(np.angle(Hsw))

        return [ zf(rxsw.fd, txsw.fd.pilots) ] + [ zf(rxsym.fd, ofdm.pilot_values) for rxsym in symbols[1:] ]
        
