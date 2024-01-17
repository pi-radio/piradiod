import numpy as np

from piradio.util import REAL_SAMPLES, IQ_SAMPLES

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

            if sbuf.sample_format == REAL_SAMPLES:
                sbuf.array = self.amplitude * np.cos(2.0 * np.pi * f.hz * sbuf.t + self.phase)
            else:
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
        
        class RealZadoffChu:
            def __init__(self, N, q, u, amplitude=1.0, timescale=1, LO_DIV=4):
                self.N = N
                self.q = q
                self.u = u
                self.amplitude = amplitude
                self.timescale = timescale
                self.LO_DIV = LO_DIV
                
            def apply(self, sbuf, nrepeat=1):
                cf = self.N % 2
                n = np.arange(self.N * self.timescale)
                
                wform = np.exp(-1.0j * np.pi * self.u * n * (n + cf + 2 * self.q) / self.N / self.timescale)
                
                # now we mix at FS/4
                LO_t = 2 * np.pi * n / self.LO_DIV
                
                wform = self.amplitude * (np.real(wform) * np.cos(n) + np.imag(wform) * -np.sin(n))
                
                if nrepeat == -1:
                    nrepeat = sbuf.nsamples // N
            
                sbuf.array = np.concatenate((np.tile(wform, nrepeat), np.zeros(sbuf.nsamples - nrepeat * len(wform))))
