import numpy as np

from piradio.util import REAL_SAMPLES, IQ_SAMPLES, GHz

class NCO:
    def __init__(self, f, sample_rate=GHz(4)):
        self.f = f
        self.sample_rate = sample_rate
        
    def mix_c2r(self, samples):
        theta = 2 * np.pi * np.arange(len(samples)) * float(self.f / self.sample_rate)
        LO = np.exp(-1.0j * theta)

        return np.real(LO * samples)

    def mix_r2c(self, samples):
        theta = 2 * np.pi * np.arange(len(samples)) * float(self.f / self.sample_rate)
        LO = np.exp(-1.0j * theta)

        return LO * samples
    

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
        def __init__(self, N, q, u, amplitude=1.0, timescale=1):
            self.N = N
            self.q = q
            self.u = u
            self.amplitude = amplitude
            self.timescale = timescale

        @property
        def wform(self):
            cf = self.N % 2

            n = np.arange(self.N * self.timescale) / self.timescale
            
            return np.exp(-1.0j * np.pi * self.u * n * (n + cf + 2 * self.q) / self.N / self.timescale)
            
        def apply(self, sbuf, nrepeat=1):
            if nrepeat == -1:
                nrepeat = sbuf.nsamples // N
            
            sbuf.array = np.concatenate((np.tile(self.wform, nrepeat), np.zeros(sbuf.nsamples - nrepeat * len(wform))))
        
    class RealZadoffChu(ZadoffChu):
        def __init__(self, N, q, u, amplitude=1.0, timescale=1, LO_DIV=4):
            super().__init__(N, q, u, amplitude, timescale)
            self.LO_DIV = LO_DIV

        @property
        def wform(self):
            wform = super().wform

            LO_t = 2 * np.pi * np.arange(self.N * self.timescale) / self.LO_DIV

            return self.amplitude * (np.real(wform) * np.cos(LO_t) + np.imag(wform) * -np.sin(LO_t))
            
            
        def apply(self, sbuf, nrepeat=1):
            wform = self.wform
            
            if nrepeat == -1:
                nrepeat = sbuf.nsamples // N
            
            sbuf.array = np.concatenate((np.tile(wform, nrepeat), np.zeros(sbuf.nsamples - nrepeat * len(wform))))

    class real:
        class AWGN:
            def __init__(self):
                pass

            def apply(self, sbuf):
                rng = np.random.default_rng()
                
                phases = rng.random(len(sbuf.array)) * 2 * np.pi
                
                noise = np.real(np.fft.fft(np.exp(-1.0j * phases)))
                
                noise /= np.max(np.abs(noise))
                
                sbuf.array = noise
