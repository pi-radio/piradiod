import numpy as np

class signals:
    class Sine:
        def __init__(self, freq, amplitude=1.0, phase=0):
            self.freq = freq
            self.amplitude = amplitude
            self.phase = phase

        def apply(self, sbuf, make_even=True):
            f = self.freq

            if make_even:
                f = sbuf.round_freq(f)
            
            sbuf.array = self.amplitude * np.exp(1j * (-2.0 * np.pi * f.hz * sbuf.t + self.phase)) 

    class ZadoffChu:
        def __init__(self, N, q, u):
            self.N = N
            self.q = q
            self.u = u

        def apply(self, sbuf, nrepeat=1):
            cf = self.N % 2
            n = np.arange(self.N)

            wform = np.exp(-1.0j * np.pi * self.u * n * (n + cf + 2 * self.q) / self.N)

            if nrepeat == -1:
                nrepeat = sbuf.nsamples // N
            
            sbuf.array = np.concatenate((np.tile(wform, nrepeat), np.zeros(sbuf.nsamples - nrepeat * len(wform))))
        
