import numpy as np

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

    def estimate_symbol_cfo(self, symbol):
        A = symbol[:self.ofdm.CP_len]
        B = symbol[-self.ofdm.CP_len:]

        s = np.sum(A * np.conjugate(B))

        return np.angle(s)
        
    def estimate_cfo(self, samples):
        return [ self.estimate_symbol_cfo(samples[p:p+self.ofdm.symbol_len]) for p in range(0, len(samples), self.ofdm.symbol_len) ]
            

    def eq_cfo_symbol(self, symbol):
        cfo_est = self.estimate_symbol_cfo(symbol.samples) * 1.0j

        retval = symbol.stripped

        retval.cfo_est = Freq(cfo_est * self.ofdm.N / retval.samples.sample_rate.hz)
        retval.samples.samples *= np.exp(-cfo_est * np.arange(self.ofdm.N) / self.ofdm.N)
        
        return retval
            
    def eq_cfo(self, frame):
        return [ self.eq_cfo_symbol(symbol) for symbol in frame.symbols ]
            

    def eq_zf(self, symbols):
        # The first symbol is the sync_word, let's get an overall channel estimate from it just for kicks

        tx_sync_word = FDSymbol(self.ofdm, np.fft.fftshift(self.ofdm.sync_word.ft))
        rx_sync_word = symbols[0].fd
                
        H_sync_word = rx_sync_word.data_subcarriers * tx_sync_word.data_subcarriers

        Hs = [ H_sync_word ]

        eq_results = [ rx_sync_word.data_subcarriers / H_sync_word ]
        
        for sym in symbols[1:]:
            rx_word = sym.fd

            H = rx_word.pilots * np.conjugate(self.ofdm.pilot_values)

            mag = np.abs(H)
            arg = np.angle(H)

            mag_interp = np.interp(self.ofdm.data_idxs, self.ofdm.pilot_idxs, mag)
            arg_interp = np.interp(self.ofdm.data_idxs, self.ofdm.pilot_idxs, arg)

            plt.plot(self.ofdm.pilot_idxs, mag)
            plt.plot(self.ofdm.data_idxs, mag_interp)
            plt.show()

            plt.plot(self.ofdm.pilot_idxs, arg)
            plt.plot(self.ofdm.data_idxs, arg_interp)
            plt.show()

            H_recon = mag * np.exp(arg * 1.0j)

            pilot_recon = rx_word.pilots / H_recon

            plot_IQ(pilot_recon, title="Reconstructed pilots")
                        
            H_interp = mag_interp * np.exp(arg_interp * 1.0j)

            Hs.append(H_interp)

            plt.suptitle("Unadjusted subcarriers", fontsize="x-large")
            plt.scatter(np.real(rx_word.data_subcarriers), np.imag(rx_word.data_subcarriers), s=1)
            plt.show()

            plt.suptitle("Interpolated Transfer Function", fontsize="x-large")
            plt.scatter(np.real(H_interp), np.imag(H_interp), s=1)
            plt.show()
            
            w = rx_word.data_subcarriers / H_interp

            plt.suptitle("IQ", fontsize="x-large")
            plt.scatter(np.real(w), np.imag(w), s=1)
            plt.show()
            
            eq_results.append(w)


        return (eq_results, Hs)
            
