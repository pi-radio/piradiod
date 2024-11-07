from piradio.devices.sivers.eder.child import EderChild

class Beamformer(EderChild):
    def __init__(self, eder, book):
        super().__init__(eder)
        self._book = book
        self._omni = True
        self._azimuth = 0.0
        self._table = self._book[0]
        self.load_weights()
        
    def load_weights(self, table=None):
        if table is None:
            self._table = self._book[self.freq]
        else:
            self._table = table
            
        for i, wv in enumerate(self._table.wvecs):
            self.beamweights_reg[i].set(wv.to_register)
            
    def update_beamformer(self, i=None):
        if i is None:
            i = self._table.get_index(azimuth=self._azimuth, omni=self._omni)
            
        self._index = i 
        self.bf_idx_reg = self._index
        
    @property
    def omni(self):
        return self._omni

    @omni.setter
    def omni(self, v):
        self._omni = v
        self.update_beamformer()
        
    @property
    def azimuth(self):
        return self._weights.azimuth
        
    @azimuth.setter
    def azimuth(self, v):
        self._omni = False
        self._azimuth = v
        self.update_beamformer()

    @property
    def freq(self):
        return self.eder.freq
        

        
class Beambook:
    def __init__(self, *args):
        self.table = args

    def get_table(self, freq):
        freq /= 1e6
        return min(self.table, key=lambda x: abs(x.freq - freq))

    def __getitem__(self, freq):
        return self.get_table(freq)
    
class BeamformingTable:
    def __init__(self, freq, *args):
        self.freq = freq
        self.wvecs = args

    @classmethod
    def from_complex(cls, wtable):
        return cls(0.0, *[ BeamWeights.from_complex(v) for v in wtable ])
        
    def get_index(self, azimuth=0.0, omni=False):
        if omni:
            for i, w in enumerate(self.wvecs):
                if w.omni:
                    return i

        return min(enumerate(self.wvecs), key=lambda x: abs(x[1].azimuth - azimuth))[0]
        
                
    def get_weights(self, azimuth=0.0, omni=False):
        if omni:
            for wv in self.wvecs:
                if wv.omni:
                    return wv

        return min(self.weights, key=lambda x: abs(x.azimuth - azimuth))

    @property
    def weight_data(self):
        retval = b''

        for wv in self.wvecs:
            for w in wv.weights:
                retval += w.to_bytes(2, 'big')

        return retval

    def __repr__(self):
        return f"<Table: freq: {self.freq} " + " ".join([ str(wv) for wv in self.wvecs ]) + ">"
        
class BeamWeights:
    def __init__(self, weights, azimuth=0.0, omni=False):
        self.weights = weights
        self.azimuth = azimuth
        self.omni = omni

    @classmethod
    def from_complex(cls, wv):
        a = []

        for w in wv:
            a += [ int(round((w.imag + 1) * 31.5)),
                   int(round((w.real + 1) * 31.5)) ]

        return cls(a)
        
    @property
    def to_register(self):
        b = []
        
        for q, i in zip(self.weights[::2], self.weights[1::2]):
            v = (i << 6) | q
            b += [ v >> 8, v & 0xFF ]

        return b
            
    def __repr__(self):
        return f"<{self.weights} {self.azimuth} {self.omni}>"
