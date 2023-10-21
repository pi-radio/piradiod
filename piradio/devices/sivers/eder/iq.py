from piradio.output import output
from .adc import ADC

class DPMeasurement:
    def __init__(self, P, N):
        self.P = P
        self.N = N
        self.diff = self.P - self.N
        self.vcm = (self.P + self.N) / 2

    def meas_dco(self, adc, dco_r, dco_dcsc_r, l2samp):
        self.dco = adc.acquire(dco_r, l2samp).mean
        self.dco_dcsc = adc.acquire(dco_dcsc_r, l2samp).mean
        self.dco_diff = self.dco - self.dco_dcsc

    def meas_dco_noise(self, adc, dco_r, dco_dcsc_r, l2samp):
        self.dco_min = adc.acquire(dco_r, l2samp).min
        self.dco_dcsc_min = adc.acquire(dco_dcsc_r, l2samp).min
        
        self.dco_max = adc.acquire(dco_r, l2samp).max
        self.dco_dcsc_max = adc.acquire(dco_dcsc_r, l2samp).max
        
    @classmethod
    def read(cls, adc, P, N, l2samp=4):
        return DPMeasurement(adc.acquire(P, l2samp).mean,
                             adc.acquire(N, l2samp).mean)

    def __repr__(self):
        if hasattr(self, "dco"):
            return f"<P: {self.P} N: {self.N} diff: {self.diff} vcm: {self.vcm} dco: {self.dco} dco_dcsc: {self.dco_dcsc}: diff: {self.dco_diff}>"
            
        return f"<P: {self.P} N: {self.N} diff: {self.diff} vcm: {self.vcm}>"
    
class IQMeasurement:
    def __init__(self, I, Q):
        self.I = I
        self.Q = Q
        self.scale = 1

    @property
    def dco_diff(self):
        return self.I.dco_diff + 1.0j * self.Q.dco_diff
        
    @classmethod
    def read(cls, adc, I_P, I_N, Q_P, Q_N, l2samp):
        return IQMeasurement(DPMeasurement.read(adc, I_P, I_N, l2samp),
                             DPMeasurement.read(adc, Q_P, Q_N, l2samp))

    def __repr__(self):
        return f"<I: {self.I},\n Q: {self.Q}>"


def measure_diff_pair(adc, adc1, adc2, l2samp=4):
    return DPMeasurement.read(adc, adc1, adc2, l2samp)

RX_IQ = [ ADC.rx_bb_outb_dc_p_i, ADC.rx_bb_outb_dc_n_i, ADC.rx_bb_outb_dc_p_q, ADC.rx_bb_outb_dc_n_q ] 

def measure_IQ(adc, adc_channels, l2samp=4):
    return IQMeasurement.read(adc, *adc_channels, l2samp)
