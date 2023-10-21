import time

from piradio.output import output
from piradio.devices.sivers.eder.child import EderChild
from piradio.devices.sivers.eder.registers import attach_registers, set_bits, clear_bits, toggle_bits, modify_bits

class FreqRef(EderChild):
    def __init__(self, eder, freq=45e6):
        super().__init__(eder)
        self.freq = freq

    def startup(self):
       self.regs.bias_ctrl = set_bits(0x1c)
       self.regs.bias_pll = set_bits(0x07)
       self.regs.pll_en = set_bits(0x08)

       self.regs.fast_clk_ctrl = 0x20
       self.regs.pll_ref_in_lvds_en = 0x1

       output.debug(f"SIVERS: Ref Clk {self.freq:.2f} MHz")

       # Write monitor enable/disable

    @property
    def dig_freq(self):
        if self.regs.fast_clk_ctrl & 0x10:
            return self.freq * 5
        else:
            return self.freq * 4

    def dig_cycles(self, us):
        return round(us * self.dig_freq / 1e6)

class VCO(EderChild):
    bias_vco_x3_lo_freq = 61.29e9
    bias_vco_x3_hi_freq = 68.31e9
    
    def __init__(self, pll):
        super().__init__(pll.eder)

    def set_bias_vco_x3(self, freq):
        if self.eder.mmf:
            if freq <= self.bias_vco_x3_lo_freq or freq >= self.bias_vco_x3_hi_freq:
                self.regs.bias_vco_x3 = 0x02
            else:
                self.regs.bias_vco_x3 = 0x01
                
    
class PLL(EderChild):
    alc_table = {
        58.32: [ 0x17,0x17,0x17 ],
        60.48: [ 0x17,0x17,0x17 ],
        62.64: [ 0x17,0x17,0x17 ],
        64.80: [ 0x17,0x17,0x17 ],
        66.96: [ 0x17,0x17,0x17 ],
        69.12: [ 0x17,0x17,0x17 ]
    }

    alc_th_v=1.244               # VCO amplitude threshold = 1.196 V @ 25 degC
    atc_hi_th_v=2.4             # High tune voltage threshold = 2.4V
    atc_lo_th_v=0.4             # Low tune voltage threshold = 0.4V
    alc_th=102
    #atc_hi_th=191
    atc_lo_th=34
    dac_ref=2.8                 #Changed from 3.0 to 2.8 in Rev. B MMF
    a_freq=0
    vtune=0
    t=-273
    adc_ref_volt = 1.1
    adc_max      = 4095
    adc_scale    = 3
    adc_num_samp = 256
    temp_k       = 4e-3

    pll_en_divn = (1 << 0)
    pll_en_div2 = (1 << 1)
    pll_en_leak = (1 << 2)
    pll_en_ld   = (1 << 3)
    pll_en_chp  = (1 << 4)
    pll_en_pfd  = (1 << 5)

    
    def __init__(self, eder):
        super().__init__(eder)
        self.vco = VCO(self)
        self._freq = 0.0
    
    def freq_to_divn(self, freq):
        return int(freq/6/self.eder.ref.freq-36)

    def divn_to_freq(self, divn):
        return (divn+36)*6*self.eder.ref.freq

    def reset(self):
        self.regs.vco_tune_ctr = set_bits(0xFF)
        self.regs.vco_tune_ctrl = clear_bits(0xFF)

    def startup(self):
        self.regs.bias_ctrl = set_bits(0x7F)
        self.regs.bias_pll = 0x17
        self.regs.bias_lo = 0x2a

        self.regs.pll_ref_oin_lvds_en = 0x01
        self.regs.pll_en = 0x7b
        self.regs.pll_chp = 1

        self.regs.vco_alc_del = 0x0e
        self.regs.vco_tune_loop_del = 0x000384
        self.regs.vco_atc_vtune_set_del = 0x001194
        self.regs.vco_atc_vtune_unset_del = 0x000384

        self.regs.vco_vtune_ctrl = 0x20

        # VCO amplitude threshold
        self.regs.vco_alc_hi_th = int(self.alc_th_v/self.dac_ref*255)
        self.regs.vco_atc_hi_th = int(self.atc_hi_th_v/self.dac_ref*255)
        self.regs.vco_atc_lo_th = int(self.atc_lo_th_v/self.dac_ref*255)

        self.regs.pll_pfd = 0x00
        self.regs.vco_en = 0x3c
        
        self.regs.vco_tune_ctrl = set_bits(1<<2)

        time.sleep(0.5)

        output.debug("PLL initialized")

    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, f):
        output.info(f'Setting frequency to {f/1e9} GHz')

        self.vco.set_bias_vco_x3(f)

        T = self.eder.adc.tj-273

        output.info(f'Temperature: {T:1.3f} C')

        # Set vco amplitude according to temperature 
        self.alc_th=int((self.alc_th_v + (25-T)*2.4e-3)/self.dac_ref*255)  # VCO amplitude threshold
        
        self.regs.vco_alc_hi_th = self.alc_th
        
        if self.eder.mmf:
            #Set vtune_th according to temperature
            vtune_th=int((T*9e-3+1.166)*255/self.dac_ref)
            #pll_chp is set to 0x01 before lock
            self.regs.pll_chp = clear_bits(0x03)
            self.regs.pll_chp = set_bits(0x01)
        else:
            self.vtune_th=int((T*67e-4+1.066)*255/self.dac_ref)
            
        self.regs.vco_vtune_atc_lo_th = vtune_th

        divn = self.freq_to_divn(f)

        self.regs.pll_divn = self.freq_to_divn(f)
        
        self.regs.vco_tune_ctrl = toggle_bits(0x02)
        self.regs.vco_tune_ctrl = toggle_bits(0x01)

        # Increased to 2 ms from 0.5 ms
        time.sleep(0.002)
        
        if self.eder.mmf:
            #Set pll_chp to 0x00 if digtune between 28 and 64 or 92 and 128
            digtune=self.regs.vco_tune_dig_tune
            if (0x5C < digtune) or (0x1D < digtune < 0x40):
                self.regs.pll_chp = clear_bits(0x03)

        vco_tune_status = self.regs.vco_tune_status
        vco_tune_det_status = self.regs.vco_tune_det_status
        vco_tune_freq_cnt = self.regs.vco_tune_freq_cnt
                
        # Check if tuning has succeeded
        if ((vco_tune_status != 0x7e) or
            (vco_tune_det_status & 0x01 != 0x01) or
            (vco_tune_freq_cnt > 0x80a) or
            (vco_tune_freq_cnt < 0x7f4)):
            output.info('VCO tune FAILED')
        else:
            self.regs.vco_tune_ctrl = set_bits(0x04)

        readback = self.regs.pll_divn
        
        self._freq = self.divn_to_freq(self.regs.pll_divn)

        print(f"Tuned to frequency: {self._freq}")
            
        #self.monitor('Vtune')
        

    @property
    def vtune(self):
        dac = 128
        for x in range(8):
            self.regs.vco_atc_hi_th = dac

            if self.regs.vco_tune_det_status >= 8:
                dac = int(dac + 2**(6-x))
            else:
                dac = int(dac - 2**(6-x))


        self.regs.vco_atc_hi_th = int(self.atc_hi_th_v/self.dac_ref * 255)

        return dac * self.dac_ref / 255

    @property
    def vcoamp(self):
        dac = 128
        for x in range(8):
            self.regs.vco_alc_hi_th = dac

            if self.regs.vco_tune_det_status & 2:
                dac = int(dac + 2**(6-x))
            else:
                dac = int(dac - 2**(6-x))

        self.regs.vco_alc_hi_th = int(self.atc_hi_th_v/self.dac_ref * 255)

        return dac * self.dac_ref / 255
