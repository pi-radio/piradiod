from functools import cached_property

import numpy as np
import matplotlib.pyplot as plt

from piradio.util import Samples

from .symbol import FullSymbol


rng = np.random.default_rng()

class SimChannel:
    def __init__(self, ofdm, tx_gain, cfo, noise_sigma):
        self.cfo = cfo
        self.ofdm = ofdm
        self.noise_sigma = noise_sigma
        self.tx_gain = tx_gain
        
    def distort_symbol(self, symbol):
        signal = self.tx_gain * symbol.samples * np.exp(-2 * np.pi * 1.0j * self.cfo / self.ofdm.sample_rate * np.arange(len(symbol.samples)))

        signal = signal + rng.normal(0, self.noise_sigma / 2, len(symbol.samples)) + 1.0j * rng.normal(0, self.noise_sigma / 2, len(symbol.samples))
        
        return self.ofdm.full_symbol(Samples(signal, self.ofdm.sample_rate))
        
