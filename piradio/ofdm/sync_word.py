import numpy as np

from .symbol import Frame


sync_word_bits_in = [0x6b,0x3c,0x87,0xf2,0x30,0x8d,0x00,0x20,0x7d,0xbf,0x1b,0x89,0x42,0x97,0xec,0x79,0x0f,0x27,0x41,0x3e,0x5e,0x17,0x9c,0x8d,0x7c,0x76,0xbe,0x26,0x07,0x39,0x46,0xcf,0x54,0x47,0x5d,0x7a,0x28,0x12,0xe8,0x2b,0x06,0x28,0x25,0x13,0x09,0x2d,0x4b,0x8b,0x14,0x0b,0xf8,0x75,0x15,0xbf,0xdb,0x85,0x62,0xc8,0xf6,0x0f,0x79,0x0f,0xc2,0xb7,0x34,0x24,0x1c,0x66,0x57,0x13,0x04,0x64,0x2f,0xee,0xc4,0x05,0x4a,0x66,0x1b,0x7f,0x47,0xbc,0xab,0xbe,0x7e,0x7b,0xfc,0xc4,0x76,0xc4,0x0a,0xb4,0x38,0x1d,0xc2,0x71,0x0a,0xfa,0x2c,0x4b];

sync_iter = iter(sync_word_bits_in)

#sync_word_bits = [ (a << 24) | (b << 16) | (c << 8) | d for a, b, c, d in zip(sync_iter, sync_iter, sync_iter, sync_iter) ]
#print("[ " + ",".join([ f"0x{x:08x}" for x in sync_word_bits ]) + " ]")
    

class SyncWord:
    bits = [
        0x6b3c87f2,
        0x308d0020,
        0x7dbf1b89,
        0x4297ec79,
        0x0f27413e,
        0x5e179c8d,
        0x7c76be26,
        0x073946cf,
        0x54475d7a,
        0x2812e82b,
        0x06282513,
        0x092d4b8b,
        0x140bf875,
        0x15bfdb85,
        0x62c8f60f,
        0x790fc2b7,
        0x34241c66,
        0x57130464,
        0x2feec405,
        0x4a661b7f,
        0x47bcabbe,
        0x7e7bfcc4,
        0x76c40ab4,
        0x381dc271,
        0x0afa2c4b
    ]

    default_word = [ 1.0 if w & (1 << b) else -1.0 for w in bits for b in range(32) ]

    def __init__(self, ofdm):
        self.ofdm = ofdm
        self.sync_word = self.default_word

        lo_pad = [ 0 ] * ofdm.LO_space
        guard_pad = [ 0 ] * ofdm.N_guard_band
        
        self.ft = np.fft.fftshift(np.array(guard_pad + self.sync_word[:len(self.sync_word)//2] + lo_pad + self.sync_word[len(self.sync_word)//2:] + guard_pad,
                                           dtype=np.cdouble))

        assert len(self.ft) == ofdm.N, f"WTF: {len(self.ft)} {ofdm.LO_space} {ofdm.N_guard_band}"
        
        td = np.fft.ifft(self.ft)

        self.sync_word_td = np.concatenate((td[-len(td)//4:], td))

    @property
    def subcarriers(self):
        return np.fft.fftshift(self.ft)[self.ofdm.N_guard_band:-self.ofdm.N_guard_band]
        
    def correlate(self, v):
        if hasattr(v, "fft"):
            v = v.fft

        return np.fft.ifft(v * np.conj(self.ft))

    def synchronize(self, s, threshold=2.0, frame_symbols=1):
        sync_pos = []

        for pos in range(0, len(s)-self.ofdm.N+1, self.ofdm.N//2):
            window = s[pos:pos+self.ofdm.N]

            c = self.correlate(window.spectrum)

            offset = np.argmax(np.abs(c))
            score = np.max(np.abs(c))

            if score > threshold:
                print(f"Alignment at {pos+offset}: score: {score}")
                if pos + offset not in sync_pos:
                    sync_pos.append(pos+offset)

                if len(sync_pos) == 2:
                    break

        pos = sync_pos[1]-self.ofdm.symbol_len
        
        return Frame(self.ofdm, s[pos:pos+self.ofdm.frame_len])
    
        

