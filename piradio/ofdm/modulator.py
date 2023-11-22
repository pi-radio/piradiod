import numpy as np

from piradio.util import Samples

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

        mod_data = [ 1 if d else -1 for d in data ]
        
        sym.data_subcarriers = mod_data

        return sym
    
    def random_data(self):
        return rng.choice([1, 0], self.ofdm.NDSC)

    @property
    def data_rate(self):
        return len(self.ofdm.data_idxs) * self.ofdm.frame_symbols / self.ofdm.frame_time
        
