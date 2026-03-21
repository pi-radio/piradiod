import numpy as np

from functools import cached_property

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

def mult_inv(n, p):
    euclid = [ [ p, 1, 0 ], [ n, 0, 1 ] ]
    
    while True:
        r0, s0, t0 = euclid[-2]
        r1, s1, t1 = euclid[-1]

        q, r = np.divmod(r0, r1)

        if r == 0:
            return t1        
        
        rn = (r0 - q * r1) % p
        sn = (s0 - q * s1) % p
        tn = (t0 - q * t1) % p

        #print(f"q: {q} r: {r} rn: {rn} sn: {sn} tn: {tn}")

        euclid += [ [ r, sn, tn ] ]

def issquare(n):
    x = n//2
    seen = set([x])
    
    while x*x != n:
        x = (x + (n // x)) // 2
        if x in seen:
            return False
        seen.add(x)
        
    return True
    
        
def legendre_symbol(n, N):
    n = n % N
    
    if n == 0:
        return 0
    
    if issquare(n):
        return 1
    
    return -1    
    
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

    class ZCSequence:
        def __init__(self, Nzc, u):
            self.Nzc = Nzc
            self.u = u

            n = np.arange(self.Nzc)
        
            self._symbols = np.exp(-1.0j * np.pi * self.u * n * (n + 1) / self.Nzc)

        @property
        def symbols(self):
            return self._symbols

        @cached_property
        def ft(self):
            if self.Nzc % 4 == 1:
                eta = 1
            else:
                eta = -1.0j
                
            Xu0 = (legendre_symbol(2 * self.u, self.Nzc) * 
                   eta * 
                   np.sqrt(self.Nzc) * np.exp(1.0j * 2 * np.pi * self.u / self.Nzc * ((self.Nzc+1)/2)**3))
            
            uinv = mult_inv(self.u, self.Nzc)

            return Xu0 * np.conjugate(self.symbols[(uinv * np.arange(self.Nzc)) % self.Nzc])

        def interpolate(self, N):
            ft = np.zeros(N, dtype=np.complex128)

            d = self.Nzc // 2
            
            ft[:d+1] = self.ft[:d+1]
            ft[-d:] = self.ft[d+1:]

            signal = np.fft.ifft(ft)
            
            return signal / np.max(np.abs(signal))

        def apply(self, sbo):
            sbo.array = self.interpolate(len(sbo.array))          
            
            

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
