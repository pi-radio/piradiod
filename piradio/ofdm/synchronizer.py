import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import find_peaks

from piradio.util import Samples


from .symbol import Frame, FDSymbol


class Synchronizer:
    def __init__(self, ofdm):
        self.ofdm = ofdm


    def synchronize_CP(self, rx_samp):
        A = rx_samp[:-self.ofdm.N]
        B = rx_samp[self.ofdm.N:]

        C = A * np.conj(B)

        r = np.convolve(C, np.ones(self.ofdm.CP_len), mode="valid")

        p, _ = find_peaks(r, distance=self.ofdm.N)

        # Not completely correct, as it helps find symbols
        print(f"CP SYNC: {p[0]}")

        return self.ofdm.frame(rx_samp[p[0]:p[0]+self.ofdm.frame_len])
        

    def synchronize(self, rx_samp):
        peak = None
        best_score = 0
        
        for i in range(2 * len(rx_samp) // self.ofdm.N - 1):
            pos = i * self.ofdm.N//2

            samples = rx_samp[pos:pos+self.ofdm.N]

            v = np.fft.ifft(np.fft.fft(samples) * self.ofdm.sync_word.fd.fft)
            
            new_peak = np.argmax(np.abs(v)) + pos - self.ofdm.CP_len
            score = np.max(np.abs(v))
            
            if score > best_score:
                print(f"New score: {new_peak} {score}")
                if best_score != 0 and np.abs(peak + self.ofdm.N - new_peak) <= 1:
                    new_peak -= self.ofdm.N
                
                peak = new_peak
                best_score = score

        print(f"Peak: {peak} Score: {score}")

        return self.ofdm.frame(rx_samp[peak:peak+self.ofdm.frame_len])

        
