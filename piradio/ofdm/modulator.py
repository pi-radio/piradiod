import numpy as np

from piradio.util import Samples

from .symbol import FDSymbol

rng = np.random.default_rng()

class Modulator:
    pass

rng = np.random.default_rng()

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
        
class QAM(Modulator):
    def __init__(self, N):
        self.N = N
        self.l2N = np.log2(N)
        
        assert self.l2N == np.floor(self.l2N), "Non-power-of-two QAM not yet handled"

        self.l2N = int(self.l2N)
        
        assert self.l2N & 1 == 0, "Non even constellation not handled yet"

        self.w = self.l2N // 2
        
        p1 = np.array([ 1 - x / (1 << self.w) for x in range(1 << self.w) ])
        
        self.constellation_points = np.concatenate((-p1, np.flip(p1)))

    def modulate_sym_bits(self, sym_seq):
        return [ self.constellation_points[(x & ((1 << self.w) - 1))] +
                 1.0j * self.constellation_points[(x >> self.w)] for x in sym_seq ]

    def generate_random_syms(self, N):
        return self.modulate_sym_bits(rng.integers(low=0, high=((1 << (2*self.w))-1), size=N))
