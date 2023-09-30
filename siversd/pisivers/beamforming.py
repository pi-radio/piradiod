from piradio.devices.sivers.eder.child import EderChild

class Beamformer(EderChild):
    def __init__(self, eder, book):
        super().__init__(eder)
        self._book = book
        self._omni = True
        self._azimuth = 0.0
        self._table = self._book[0]
        self.load_weights()
        
    def load_weights(self):
        self._table = self._book[self.freq]
        for i, wv in enumerate(self._table.wvecs):
            self.beamweights_reg[i].set(wv.weights)
            
    def update_beamformer(self):
        self._index = self._table.get_index(azimuth=self._azimuth, omni=self._omni)
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
        freq /= 1e3
        print(f"Searching for freq {freq}")
        return min(self.table, key=lambda x: abs(x.freq - freq/1e3))

    def __getitem__(self, freq):
        return self.get_table(freq)
    
class BeamformingTable:
    def __init__(self, freq, *args):
        self.freq = freq
        self.wvecs = args

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

    def __repr__(self):
        return f"<{self.weights} {self.azimuth} {self.omni}>"
