import numpy as np

from .symbol import FDSymbol

rng = np.random.default_rng()

class Modulator:
    pass

class BPSK(Modulator):
    def __init__(self, ofdm):
        self.ofdm = ofdm

    def modulate(self, data):
        sym = FDSymbol(self.ofdm)

        sym.pilots = self.ofdm.pilot_values
        sym.data_subcarriers = data
        
        td = np.fft.ifft(np.fft.fftshift(sym.fft))

        return np.concatenate((td[-self.ofdm.CP_len:], td))
    
    def random_data(self):
        return rng.choice([1, -1], 600)
        
