import numpy as np
import matplotlib.pyplot as plt

from .samples import Samples

class FIR:
    def __init__(self, coeff):
        self._coeff = coeff

    @property
    def coeff(self):
        return self._coeff

    @property
    def n(self):
        return len(self._coeff)
    
    def apply(self, samples, circular=True):
        if isinstance(samples, Samples):
            a = samples.samples
        else:
            a = samples

        if circular:
            s = np.concatenate((a[-self.n:], a, a[:self.n]))
        else:
            s = np.concatenate(([0] * self.n, a, [ 0 ] * self.n))
            
        result = np.convolve(s, self.coeff, mode="valid")

        if isinstance(samples, Samples):
            return Samples(result, sample_rate=samples.sample_rate)
        else:
            return result

    def freq_response(self, N, sample_rate):
        a = np.zeros(N)

        a[:self.n] = self.coeff

        ft = np.fft.fftshift(np.fft.fft(a))
        freq = np.fft.fftshift(np.fft.fftfreq(N, d=(1/sample_rate).s))
        
        mag = np.abs(ft)
        mag[mag == 0] = 1e-10

        mag = 20 * np.log10(mag)
        
        arg = 360 * np.angle(ft) / 2 / np.pi

        plt.plot(freq/1e6, mag)
        plt.show()
        plt.plot(freq/1e6, arg)
        
        
