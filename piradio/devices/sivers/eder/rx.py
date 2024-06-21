import numpy as np
import time
from contextlib import contextmanager

from piradio.output import output
from piradio.devices.sivers.eder.registers import attach_registers, set_bits, clear_bits
from piradio.devices.sivers.eder.child import EderChild
from .iq import RX_IQ, measure_IQ 
from .beamforming import Beamformer
from .BFM06010 import RXWeights

class RXChannel(EderChild):
    def __init__(self, rx):
        self.rx = rx
        super().__init__(rx.eder)    

    def drv_cal(self):
        found = False
        
        start_dco = -31
        end_dco = 31

        self.drv_offset = start_dco
        start_meas = self.dco_diff

        self.drv_offset = end_dco
        end_meas = self.dco_diff

        if np.sign(start_meas) == np.sign(end_meas):
            output.warn(f"Unable to fully adjust RX {self.name} DCO Drive control -- out of range {self.start_meas} {self.end_meas}")
            
            if abs(self.start_meas) < abs(self.end_meas):
                self.cal_offset = start_dco
            else:
                self.cal_offset = end_dco

            return
        
        while abs(end_dco - start_dco) > 1:
            output.debug(f"{self.name} DCO Drive Range: {start_dco}-{end_dco}=>{start_meas}-{end_meas}")
            mean_dco = int(round((start_dco + end_dco) / 2))
            self.drv_offset = mean_dco
            mean_meas = self.dco_diff

            if np.sign(mean_meas) != np.sign(start_meas):
                end_dco = mean_dco
                end_meas = mean_meas
            elif np.sign(mean_meas) != np.sign(end_meas):
                start_dco = mean_dco
                start_meas = mean_meas
            else:
                raise RuntimeError("Drive control search broken")

        if abs(start_meas) < abs(end_meas):
            self.cal_offset = start_dco
        else:
            self.cal_offset = end_dco
            

    def dco_find(self):
        for mult in [ (i << 12) for i in range(4) ]:
            for shift in [ (i << 8) for i in range(3) ]:
                self.dco_reg = mult | shift
                v0 = self.dco_diff
                self.dco_reg = mult | shift | 0x7F
                v1 = self.dco_diff

                output.debug(f"dco_find: mult: {mult} shift: {shift} {v0}-{v1}")
                
                if np.sign(v0) != np.sign(v1):
                    return mult, shift

        raise RuntimeError("RX DCO calibration failed")

                
    def dco_cal(self):
        mult, shift = self.dco_find()
        
        start_dco = 0
        end_dco = 0x7F

        self.dco_reg = mult | shift | start_dco
        start_diff = self.dco_diff
        
        self.dco_reg = mult | shift | end_dco
        end_diff = self.dco_diff

        while abs(end_dco - start_dco) > 1:
            output.debug(f"dco: {start_dco}-{end_dco} meas: {start_diff}-{end_diff}")
            mean_dco = int(round((start_dco + end_dco) / 2))
            self.dco_reg = mult | shift | mean_dco
            diff = self.dco_diff

            if np.sign(diff) == np.sign(start_diff):
                start_dco = mean_dco
                start_diff = diff
            elif np.sign(diff) == np.sign(end_diff):
                end_dco = mean_dco
                end_diff = diff
            elif diff == 0:
                self.cal_dco_reg = mult | shift | mean_dco
                return
            else:
                raise RuntimeError("DCO search broken")

        if abs(end_diff) < abs(start_diff):
            self.cal_dco_reg = mult | shift | end_dco
        else:
            self.cal_dco_reg = mult | shift | start_dco


    @property
    def dco(self):
        return self.meas.dco

    @property
    def dco_diff(self):
        return self.meas.dco_diff

    def do_meas(self):
        meas = self.rx.measure_dco()        
        return meas

    @property
    def drv_offset(self):
        return (self.regs.rx_drv_dco >> self.drv_shift) & 0x3F
        
    @drv_offset.setter
    def drv_offset(self, v):
        if v < 0:
            v = 32 - v
        self.regs.rx_drv_dco = clear_bits(0x3F << self.drv_shift)
        self.regs.rx_drv_dco = set_bits((v & 0x3F) << self.drv_shift)

    
class RX_I(RXChannel):
    name = "I"
    drv_shift = 14
    
    @property
    def dco_reg(self):
        return self.regs.rx_bb_i_dco

    @dco_reg.setter
    def dco_reg(self, v):
        self.regs.rx_bb_i_dco = v
    
    @property
    def meas(self):        
        return self.do_meas().I

        
class RX_Q(RXChannel):
    name = "Q"
    drv_shift = 8
                
    @property
    def dco_reg(self):
        return self.regs.rx_bb_q_dco

    @dco_reg.setter
    def dco_reg(self, v):
        self.regs.rx_bb_q_dco = v

    @property
    def meas(self):
        return self.do_meas().Q

def vga12_to_gain(v):
    return { 0xF: 21, 0x7: 18, 0x3: 12, 0x1: 6, 0x0: 0 }[v]

def vga3_to_gain(v):
    return v / 15 * 6

def gain_to_vga12(g):
    if g == 21:
        return 0xF
    if g == 18:
        return 0x7
    if g == 12:
        return 0x3
    if g == 6:
        return 0x1
    if g == 0:
        return 0x0
    raise RuntimeError("Invalid VGA1/2 gain")

def gain_to_vga3(g):
    return max(min(int(g * 15 / 6), 15),0)
    
class RX(Beamformer):
    
    def __init__(self, eder):
        super().__init__(eder, RXWeights)
        self._omni = True

        self.I = RX_I(self)
        self.Q = RX_Q(self)
        
    @property
    def regs(self):
        return self.eder.regs

    def run_drv_cal(self):
        with self.regs.push_regs():
            self.regs.trx_ctrl = 0
            self.regs.trx_rx_on = 0x1E0000
            self.regs.trx_rx_off = 0x1E0000
            self.regs.rx_dco_en = 0x01
            self.regs.rx_bb_i_dco = 0x40
            self.regs.rx_bb_q_dco = 0x40

            self.lna_state = 0
            
            self.bfrf_gain = (0, 0)
            self.VGA1_gain = 6
            self.VGA2_gain = 6
            self.VGA3_gain = 2.8
            
            self.I.drv_cal()
            self.Q.drv_cal()

        self.I.drv_offset = self.I.cal_offset
        self.Q.drv_offset = self.Q.cal_offset

    def run_dco_cal(self):
        with self.save_regs():
            self.regs.trx_ctrl = 0x1
            self.lna_state = False

            self.I.dco_cal()
            self.Q.dco_cal()

        self.I.dco_reg = self.I.cal_dco_reg
        self.Q.dco_reg = self.Q.cal_dco_reg

    def load_gains(self):
        r = self.regs.rx_gain_ctrl_bfrf

        self._bf_gain = (r >> 4) & 0xF
        self._rf_gain = r & 0xF

        r = self.regs.rx_gain_ctrl_bb1
        
        self._I_vga1_gain = vga12_to_gain((r) & 0xF)
        self._Q_vga1_gain = vga12_to_gain((r >> 4) & 0xF)

        r = self.regs.rx_gain_ctrl_bb2
        
        self._I_vga2_gain = vga12_to_gain((r) & 0xF)
        self._Q_vga2_gain = vga12_to_gain((r >> 4) & 0xF)

        r = self.regs.rx_gain_ctrl_bb3
        
        self._I_vga3_gain = vga3_to_gain((r) & 0xF)
        self._Q_vga3_gain = vga3_to_gain((r >> 4) & 0xF)
        
        
    max_gain = 15 + 15 + 21 + 21 + 6

    @property
    def I_gain(self):
        return self._bf_gain + self._rf_gain + self._I_vga1_gain + self._I_vga2_gain + self._I_vga3_gain
    
    @property
    def Q_gain(self):
        return self._bf_gain + self._rf_gain + self._Q_vga1_gain + self._Q_vga2_gain + self._Q_vga3_gain

    @property
    def bfrf_gain(self):
        return (self._bf_gain, self._rf_gain)

    @bfrf_gain.setter
    def bfrf_gain(self, v):
        bf_gain, rf_gain = v
        output.debug(f"Setting front end gain: BF: {bf_gain} RF: {rf_gain}")
        assert (bf_gain >= 0) and (bf_gain <= 15)
        assert (rf_gain >= 0) and (rf_gain <= 15)
        self._bf_gain = int(bf_gain)
        self._rf_gain = int(rf_gain)

        self.regs.rx_gain_ctrl_bfrf = (bf_gain << 4) | (rf_gain)
        
    
    @property
    def VGA1_gain(self):
        return (self._I_vga1_gain, self._Q_vga1_gain)

    @VGA1_gain.setter
    def VGA1_gain(self, v):
        if isinstance(v, (float, int)):
            I = v
            Q = v
        else:
            assert len(v) == 2
            I = v[0]
            Q = v[1]

        output.debug(f"Setting VGA1 gain: I: {I} Q: {Q}")

        self.regs.rx_gain_ctrl_bb1 = gain_to_vga12(I) | (gain_to_vga12(Q) << 4)

        self._I_vga1_gain = I
        self._Q_vga1_gain = Q
        
    @property
    def VGA2_gain(self):
        return (self._I_vga2_gain, self._Q_vga2_gain)

    @VGA2_gain.setter
    def VGA2_gain(self, v):
        if isinstance(v, (float, int)):
            I = v
            Q = v
        else:
            assert len(v) == 2
            I = v[0]
            Q = v[1]

        output.debug(f"Setting VGA2 gain: I: {I} Q: {Q}")

        self.regs.rx_gain_ctrl_bb2 = gain_to_vga12(I) | (gain_to_vga12(Q) << 4)

        self._I_vga2_gain = I
        self._Q_vga2_gain = Q
    
    @property
    def VGA3_gain(self):
        return (self._I_vga3_gain, self._Q_vga3_gain)

    @VGA3_gain.setter
    def VGA3_gain(self, v):
        if isinstance(v, (float, int)):
            I = v
            Q = v
        else:
            assert len(v) == 2
            I = v[0]
            Q = v[1]


        output.debug(f"Setting VGA3 gain: I: {I} Q: {Q}")
            
        self.regs.rx_gain_ctrl_bb3 = gain_to_vga3(I) | (gain_to_vga3(Q) << 4)

        self._I_vga3_gain = I
        self._Q_vga3_gain = Q

    
    @property
    def gain(self):
        return (self.I_gain + self.Q_gain) / 2
    
    @gain.setter
    def gain(self, v):
        # Beamforming gain is in dB (0-15)
        # RF VGA gain is in dB (0-15)
        # VGA 1-2 allowed values 0xF == 21dB, 0x7 == 18dB, 0x3 == 12dB, 0x1 == 6dB, 0x0 == 0dB
        # VGA 3 0-15 == 0-6dB

        # Total: 15 + 15 + 21 + 21 + 6 == 78

        ov = v
        
        bf_gain = int(min(v, 15))
        v -= bf_gain

        rf_gain = int(min(v, 15))
        v -= rf_gain

        self.bfrf_gain = (bf_gain, rf_gain)        


        # We want VGA1 & VGA2 to share the load to avoid
        # interstage saturation
        
        if v >= 42:
            gain = 21
        elif v > 36:
            gain = 18
        elif v > 12:
            gain = 12
        elif v >= 6:
            gain = 6
        else:
            gain = 0
            
        v -= gain
        self.VGA1_gain = gain

        if v >= 21:
            gain = 21
        elif v >= 18:
            gain = 18
        elif v >= 12:
            gain = 12
        elif v >= 6:
            gain = 6
        else:
            gain = 0

        v -= gain
        self.VGA2_gain = gain

        if v > 6:
            output.error(f"Gain too high: {ov} max {self.max_gain}")
            v = 6

        self.VGA3_gain = v
            
            
    def startup(self):
        self.load_gains()
        
        self.regs.trx_rx_on = 0x1FFFFF
        
        if self.eder.mmf:
            self.regs.bias_rx = 0xAA9
        else:
            self.regs.bias_rx = 0xAAA

        self.regs.bias_ctrl = set_bits(0x7F)
        self.regs.bias_lo = set_bits(0x22)
        self.regs.rx_bb_biastrim = 0x00
        self.regs.rx_gain_ctrl_mode = 0x13
        self.regs.rx_dco_en = 0x01

        self.bfrf_gain = (6, 6)
        self.VGA1_gain = 18
        self.VGA2_gain = 6
        self.VGA3_gain = 2.4
        
        output.debug("RX calibrating baseband")

        self.run_drv_cal()

        self.run_dco_cal()
        
        self.regs.trx_rx_on = 0x1FFFFF
        self.regs.trx_rx_off = 0x000000
        
        self.regs.trx_ctrl = 0x0

        self.gain = 70
        
        output.info("RX startup complete")
        self.omni = True
        self.update_beamformer()
        
    def ready(self):
        pass
        
    def enable(self):
        # Go ahead and turn on the LNA
        self.lna_state = True

    def disable(self):
        # Go ahead and turn on the LNA
        self.lna_state = False
        
    @property
    def lna_state(self):
        if self.eder.mmf:
            return True if self.regs.rx_drv_dco & 1 else False

    @lna_state.setter
    def lna_state(self, v):
        if v:
            self.regs.rx_drv_dco = set_bits(1)
        else:
            self.regs.rx_drv_dco = clear_bits(1)

    @property
    def bf_idx_reg(self):
        return self.regs.bf_rx_awv_ptr

    @bf_idx_reg.setter
    def bf_idx_reg(self, v):
        self.regs.bf_rx_awv_ptr = v
    
    @property
    def beamweights_reg(self):
        return self.regs.bf_rx_awv

    def measure_bb(self, l2samp=4):
        return measure_IQ(self.eder.adc, RX_IQ, l2samp)

    def measure_dco(self, l2samp=4):
        adc = self.eder.adc
        
        retval = measure_IQ(adc, RX_IQ, l2samp)

        retval.I.meas_dco(adc, adc.dco_i, adc.dco_i_dcsc, l2samp)
        retval.Q.meas_dco(adc, adc.dco_q, adc.dco_q_dcsc, l2samp)
        
        return retval

    def measure_dco_noise(self, l2samp=5):
        adc = self.eder.adc
        
        retval = measure_IQ(adc, RX_IQ, l2samp)

        retval.I.meas_dco(adc, adc.dco_i, adc.dco_i_dcsc, l2samp)
        retval.Q.meas_dco(adc, adc.dco_q, adc.dco_q_dcsc, l2samp)

        retval.I.meas_dco_noise(adc, adc.dco_i, adc.dco_i_dcsc, l2samp)
        retval.Q.meas_dco_noise(adc, adc.dco_q, adc.dco_q_dcsc, l2samp)

        return retval


    @contextmanager
    def save_regs(self):
        regs = [
            "rx_gain_ctrl_bb1",
            "rx_gain_ctrl_bb2",
            "rx_gain_ctrl_bb3",
            "rx_gain_ctrl_bfrf",
            "rx_bb_test_ctrl",
            "bias_rx",
            "bias_lo"
        ]

        lna_state = self.lna_state
                 
        saved_regs = [ getattr(self.regs, r) for r in regs ]

        yield None

        for n, v in zip(regs, saved_regs):
            setattr(self.regs, n, v)

        self.lna_state = lna_state
    
    def loopback(self):
        self.regs.trx_rx_on = 0x1F0000;

    def loopback_off(self):
        self.regs.trx_rx_on = 0x1FFFFF;
