import time
from threading import RLock

from piradio.output import output
from piradio.devices.sivers.eder.child import EderChild
from .registers import set_bits, clear_bits, modify_bits, toggle_bits

def sign_extend(x, bits):
    sign_bit = 1 << (bits - 1)
    return (x & (sign_bit - 1)) - (x & sign_bit)

class DieTemp:
    def __init__(self, adc):
        self.adc = adc

        self.adc_max = 4096
        self.adc_scale = 3
        
        if self.adc.eder.mmf:
            # Semi-cryptic comment...
            #ADC reference measured for 12 units at T = 0 degrees,
            #Use 1.217 for other voltage measurements (found at T = 25 degrees)
            self.adc_ref_volt = 1.213                                    # [V]
            self.temp_k       = 3.6805e-3                                # [V/K]
            self.temp_offs    = 0.2052                                   # [1/V]
        else: # Eder B
            self.adc_ref_volt = 1.228                                    # [V]
            self.temp_k       = 4e-3                                     # [V/K]
            self.temp_offs    = 41e-3                                    # [K/V]

        self.temp_scale   = self.adc_scale*self.adc_ref_volt/self.adc_max/self.temp_k    # [K]
        self.temp_comp    = self.temp_offs/self.temp_k                         # [K]
        self.temp_calib_offset = 0

    def read(self):
        return self.adc.acquire(self.adc.temp).mean * self.temp_scale - self.temp_comp + self.temp_calib_offset
            
    
class ADCMux:
    def __init__(self, mux1, mux_attr=None, mux2=None):
        self.mux1 = mux1
        self.mux_attr = mux_attr
        self.mux2 = mux2

    def __getitem__(self, v):
        assert self.mux_attr is not None

        if self.mux2 is not None:
            return ADCMux(self.mux1, self.mux_attr, self.mux2 + v)

        return ADCMux(self.mux1, self.mux_attr, v)

    
class ADC(EderChild):

    adc_sample_clk = 19e6
    sample_cycle = 10


    bg_pll       = ADCMux(0)
    bg_tx        = ADCMux(1)
    bg_rx        = ADCMux(2)
    temp         = ADCMux(3)
    rx_bb        = ADCMux(4, "rx_bb_test_ctrl")
    vco          = ADCMux(5, "vco_amux_ctrl")
    vcc_pll      = ADCMux(6)
    tx_pdet      = ADCMux(7, "tx_bf_pdet_mux")
    adc_ref      = ADCMux(8)
    dco_i        = ADCMux(9)
    dco_q        = ADCMux(10)
    dco_cm       = ADCMux(11)
    otp          = ADCMux(12)
    tx_env_pdet  = ADCMux(13, "tx_bf_pdet_mux")
    vcc_pa       = ADCMux(14)
    vcc_tx       = ADCMux(15)    
    dco_i_dcsc   = ADCMux(9  | 0x40)
    dco_q_dcsc   = ADCMux(10 | 0x40)
                         
    rx_bb_mix_pd_i    = rx_bb[1]
    rx_bb_mix_pd_q    = rx_bb[2]
    rx_bb_mix_pd_th_i = rx_bb[5]
    rx_bb_mix_pd_th_q = rx_bb[6]
    rx_bb_mix_dc_p_i  = rx_bb[9]
    rx_bb_mix_dc_p_q  = rx_bb[10]
    rx_bb_mix_dc_n_i  = rx_bb[13]
    rx_bb_mix_dc_n_q  = rx_bb[14]
    rx_bb_inb_pd_i    = rx_bb[17]
    rx_bb_inb_pd_q    = rx_bb[18]
    rx_bb_inb_pd_th_i = rx_bb[21]
    rx_bb_inb_pd_th_q = rx_bb[22]
    rx_bb_inb_dc_p_i  = rx_bb[25]
    rx_bb_inb_dc_p_q  = rx_bb[26]
    rx_bb_inb_dc_n_i  = rx_bb[29]
    rx_bb_inb_dc_n_q  = rx_bb[30]
    rx_bb_vga1_pd_i    = rx_bb[33]
    rx_bb_vga1_pd_q    = rx_bb[34]
    rx_bb_vga1_pd_th_i = rx_bb[37]
    rx_bb_vga1_pd_th_q = rx_bb[38]
    rx_bb_vga1_dc_p_i  = rx_bb[41]
    rx_bb_vga1_dc_p_q  = rx_bb[42]
    rx_bb_vga1_dc_n_i  = rx_bb[45]
    rx_bb_vga1_dc_n_q  = rx_bb[46]
    rx_bb_vga2_pd_i    = rx_bb[49]
    rx_bb_vga2_pd_q    = rx_bb[50]
    rx_bb_vga2_pd_th_i = rx_bb[53]
    rx_bb_vga2_pd_th_q = rx_bb[54]
    rx_bb_vga2_dc_p_i  = rx_bb[57]
    rx_bb_vga2_dc_p_q  = rx_bb[58]
    rx_bb_vga2_dc_n_i  = rx_bb[61]
    rx_bb_vga2_dc_n_q  = rx_bb[62]
    rx_bb_vga1db_pd_i    = rx_bb[65]
    rx_bb_vga1db_pd_q    = rx_bb[66]
    rx_bb_vga1db_pd_th_i = rx_bb[69]
    rx_bb_vga1db_pd_th_q = rx_bb[70]
    rx_bb_vga1db_dc_p_i  = rx_bb[73]
    rx_bb_vga1db_dc_p_q  = rx_bb[74]
    rx_bb_vga1db_dc_n_i  = rx_bb[77]
    rx_bb_vga1db_dc_n_q  = rx_bb[78]
    rx_bb_outb_pd_i    = rx_bb[81]
    rx_bb_outb_pd_q    = rx_bb[82]
    rx_bb_outb_pd_th_i = rx_bb[85]
    rx_bb_outb_pd_th_q = rx_bb[86]
    rx_bb_outb_dc_p_i  = rx_bb[89]
    rx_bb_outb_dc_p_q  = rx_bb[90]
    rx_bb_outb_dc_n_i  = rx_bb[93]
    rx_bb_outb_dc_n_q  = rx_bb[94]

    vco_alc_th    = vco[0]
    vco_vco_amp   = vco[1]
    vco_atc_lo_th = vco[2]
    vco_atc_hi_th = vco[3]
    vco_vcc_vco   = vco[4]
    vco_vcc_chp   = vco[5]
    vco_vcc_synth = vco[6]
    vco_vcc_bb_tx = vco[7]
    vco_vcc_bb_rx = vco[8]
    
    #class TempMux(ADCMuxBase):
    otp_temp_th   = 0
    otp_vdd_1v2   = 1
    otp_vdd_1v8   = 2
    otp_vcc_rx    = 3

    reg = "vco_ot_ctrl"
        
    #class LDMux:
    pll_ld_ld     = 0
    pll_ld_xor    = 1
    pll_ld_ref    = 2
    pll_ld_vco    = 3
    pll_ld_ld_raw = 4
    pll_ld_tst_0  = 5
    pll_ld_tst_1  = 6
    
    #class PDETMux(ADCMuxBase):
    pdet          = tx_pdet[(0 << 4)]
    alc_lo_th     = tx_pdet[(1 << 4)]
    alc_hi_th     = tx_pdet[(2 << 4)]
    dig_pll_vtune = tx_pdet[(3 << 4)]

    
    #class EnvPDETMux(ADCMuxBase):
    env_pdet          = tx_env_pdet[(0 << 4)]
    env_alc_lo_th     = tx_env_pdet[(1 << 4)]
    env_alc_hi_th     = tx_env_pdet[(2 << 4)]
    env_dig_pll_vtune = tx_env_pdet[(3 << 4)]
    
    def __init__(self, eder):
        super().__init__(eder)
        self._lock = RLock()

        self._temp = DieTemp(self)

    @property
    def tj(self):
        return self._temp.read()

    def reset(self):
        self.lock()
        self.regs.adc_ctrl = toggle_bits(0x20)
        self.regs.bist_adc_mux = 0x0
        self.unlock()
        
    def startup(self):
        self.lock()
        self.regs.bias_ctrl = set_bits(0x60)

        div = int(((38 * self.adc_sample_clk) / self.eder.ref.dig_freq) - 1)

        self.regs.adc_clk_div = div
        self.regs.adc_sample_cycle = self.sample_cycle
        self.edge = 0

        self.unlock()
        
    @property
    def edge(self):
        return (self.eder.adc_ctrl >> 1) & 1

    @edge.setter
    def edge(self, b):
        self.regs.adc_ctrl = modify_bits(b, 2)

    def lock(self):
        self._lock.acquire()
        
    def unlock(self):
        self._lock.release()

    def acquire(self, val, l2samps=4):
        class A:
            def __init__(self, adc):
                self.adc = adc
                self.eder = adc.eder
                self.ready = False
                
                adc.lock()

                assert self.adc.regs.adc_ctrl & 0x80 == 0

                self.adc.regs.bist_amux_ctrl = val.mux1 | 0x80

                if val.mux_attr is not None:
                    assert val.mux2 is not None
                    setattr(adc.regs, val.mux_attr, val.mux2 | 0x80)
                    

                self.adc.regs.adc_num_samples = l2samps
                self.adc.regs.adc_ctrl = toggle_bits(0x10)

            def __del__(self):
                self.adc.regs.adc_ctrl = toggle_bits(0x20)
                self.adc.unlock()
                
            def wait(self):
                if self.ready:
                    return
                
                i = 0
                while self.adc.regs.adc_ctrl & 0x80 == 0:
                    time.sleep(0.001)
                    i += 1
                    if i == 1000:
                        raise RuntimeError("Timeout on ADC conversion")

                self.ready = True
                
            @property
            def mean(self):
                self.wait()
                return self.eder.regs.adc_mean & 0xfff

            @property
            def max(self):
                self.wait()
                return self.eder.regs.adc_max & 0xfff

            @property
            def min(self):
                self.wait()
                return self.eder.regs.adc_min & 0xfff
            
            @property
            def diff(self):
                self.wait()
                return self.eder.regs.adc_diff & 0xfff

        return A(self)
            
        
    @property
    def check_3V3(self):
        return self.acquire(self.temp).mean != 0xFFF

            
    @property
    def tx_pdet(self):
        retval = []

        self.lock()

        retval = [ self.acquire(self.pdet[i], 7).mean for i in range(0, 16) ]

        self.unlock()

        retval = [ sign_extend(x, 12) for x in retval ]
                
        return retval

    @property
    def tx_env_pdet(self):
        retval = []

        self.lock()

        retval = [ self.acquire(self.env_pdet[i], 7).mean for i in range(0, 16) ]

        self.unlock()

        retval = [ sign_extend(x, 12) for x in retval ]
        
        return retval

