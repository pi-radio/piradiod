

class Beambook:
    def __init__(self, *args):
        self.table = args

    def get_table(self, freq):
        return min(self.table, key=lambda x: abs(x.freq - freq))
        
class BeamformingTable:
    def __init__(self, freq, *args):
        self.freq = freq
        self.weights = args

    def get_weights(self, azimuth=0.0, omni=False):
        if omni:
            for w in self.weights:
                if w.omni:
                    return w

        return min(self.weights, key=lambda x: abs(x.azimuth - azimuth))
            
        
class BeamWeights:
    def __init__(self, weights, azimuth=0.0, omni=False):
        self.weights = weights
        self.azimuth = azimuth
        self.omni = omni
