import math
import copy

from .regs import LMXRegs

def chandiv(i):
    return [ 2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 72, 96, 128, 192, 256, 384, 512, 768 ][i]

def input_mult_val(i):
    if i >= 8 or i == 0 or i == 2:
        raise Exception("Invalid input multiplier value")

    return i;

class LMXVCO:
    class VCO:
        def __init__(self, sel, f_min, f_max,
                     amp_cal_min, amp_cal_max,
                     cap_ctrl_min, cap_ctrl_max,
                     gain_min, gain_max):
            self.sel = sel
            self.f_min = f_min            
            self.f_max = f_max
            self.amp_cal_min = amp_cal_min
            self.amp_cal_max = amp_cal_max
            self.cap_ctrl_min = cap_ctrl_min
            self.cap_ctrl_max = cap_ctrl_max
            self.gain_min = gain_min
            self.gain_max = gain_max
            
        def scale(self, f):
            return (f-self.f_min)/(self.f_max-self.f_min) 
        
        def cap_code(self, f):
            return max(0, min(183, int(self.cap_ctrl_min + round((self.cap_ctrl_max - self.cap_ctrl_min)*self.scale(f),0))))
        
        def amp_cal(self, f):
            return max(0, min(511, int(self.amp_cal_min+round( (self.amp_cal_max-self.amp_cal_min)*self.scale(f),0 ))))

        def gain(self, f):
            return self.gain_min + int(round((self.gain_max - self.gain_min) * self.scale(f)))
        
    VCOs = [
        VCO(1, 7500, 8600, 240, 299, 12, 164, 73, 114),
        VCO(2, 8600, 9800, 247, 356, 16, 165, 61, 121),
        VCO(3, 9800, 10800, 224, 324, 19, 158, 98, 132),
        VCO(4, 10800, 12000, 244, 383, 0, 140, 106, 141),
        #   Frequency Hole
        VCO(4, 11900, 12100, 100, 100, 0, 0, 0, 0),
        VCO(5, 12000, 12900, 146, 205, 36, 183, 170, 215),
        VCO(6, 12900, 13900, 163, 242, 6, 155, 172, 218),
        VCO(7, 13900, 15000, 244, 323, 19, 175, 182, 239),
    ]
    
    def __init__(self, LMX, PLL):
        self.LMX = LMX
        self.PLL = PLL

    @property
    def f_out(self):
        return self.PLL.f_out

    @property
    def vco_n(self):
        return self.VCO.sel
    
    @property
    def VCO(self):
        for vco in self.VCOs:
            if self.f_out >= vco.f_min and self.f_out < vco.f_max:
                return vco

        raise Exception(f"Invalid frequency {self.f_out}")

    @property
    def amp_cal(self):
        return self.VCO.amp_cal(self.f_out)

    @property
    def cap_code(self):
        return self.VCO.cap_code(self.f_out)
    
    @property
    def gain(self):
        return self.VCO.gain(self.f_out)        
        
        
class OSCSource:
    def __init__(self, freq):
        self.freq = freq

    @property
    def f_out(self):
        return self.freq

class FreqUnit:
    def __init__(self, source):
        self._source = source
        self.defaults()

    @property
    def f_in(self):
        return self._source.f_out
    
class FreqMult(FreqUnit):
    @property
    def mult(self):
        return self._v

    @mult.setter
    def mult(self, v):
        self.validate(v)
        self._v = v

    @property
    def f_out(self):
        return self.f_in * self.mult

class FreqDiv(FreqUnit):        
    @property
    def den(self):
        return self._v

    @den.setter
    def den(self, v):
        self.validate(v)
        self._v = v

    @property
    def f_out(self):
        return self.f_in / self.den

class FreqMux:
    def __init__(self, sources):
        self._sources = sources
        self.defaults()

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, i):
        assert(i >= 0 and i < len(self._sources) and self._sources[i] is not None)
        self._source = i

    @property
    def source_unit(self):
        return self._sources[self._source]

    @property
    def f_out(self):
        return self.source_unit.f_out
        
    
class OSC2X(FreqMult):
    def defaults(self):
        self.mult = 2

    def validate(self, v):
        assert(v in [1, 2])

    
class PRE_R(FreqDiv):
    def defaults(self):
        self.den = 1

    def validate(self, v):
        assert(v >= 1 and v <= 2**11)

class OSCMult(FreqMult):
    def defaults(self):
        self.mult = 1

    def validate(self, v):
        assert(v in [ 1, 3, 4, 5, 6, 7 ])

class OSC_R(FreqDiv):
    def defaults(self):
        self.den = 1

    def validate(self, v):
        assert(v >= 1 and v < 2**9)

class PLL(FreqUnit):
    def defaults(self):
        self._N = 38
        self._NUM = 750
        self._DEN = 1000

    @property
    def f_out(self):
        return self.f_in * (self.N + self.NUM / self.DEN)

    @property
    def N(self):
        return self._N

    @N.setter
    def N(self, v):
        assert(v == int(v))
        self._N = v

    @property
    def NUM(self):
        return self._NUM

    @NUM.setter
    def NUM(self, v):
        assert(v == int(v))
        self._NUM = v

    @property
    def DEN(self):
        return self._DEN

    @DEN.setter
    def DEN(self, v):
        assert(v == int(v))
        self._DEN = v

class PLL2X(FreqMult):
    def defaults(self):
        self.mult = 2

    def validate(self, v):
        assert(v in [1, 2])

class PLLDIV(FreqDiv):
    def defaults(self):
        self.den = 8

    @property
    def allowed(self):
        return [2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 72, 96, 128, 192, 256, 384, 512, 768 ]
        
    def validate(self, v):
        assert(v in self.allowed)

class PortAMux(FreqMux):
    def defaults(self):
        self.source = 2

class PortBMux(FreqMux):
    def defaults(self):
        self.source = 0

class LMXConfig:
                
    def __init__(self):
        self.OSC = OSCSource(100)
        self.OSC2X = OSC2X(self.OSC)
        self.PRE_R = PRE_R(self.OSC2X)
        self.OSCMult = OSCMult(self.PRE_R)
        self.OSC_R = OSC_R(self.OSCMult)
        self.PLL = PLL(self.OSC_R)

        self.PLLDIV = PLLDIV(self.PLL)
        self.PLL2X = PLL2X(self.PLL)
        
        self.AMUX = PortAMux([ self.PLLDIV, self.PLL, self.PLL2X ])
        self.BMUX = PortBMux([ self.PLLDIV, self.PLL ]) # Missing SYSREF, but we don't use it

        self.VCO = LMXVCO(self, self.PLL)

        self._best_lock = 1
        self._reset = 0
        self._fcal_en = 1
        
    @property
    def regs(self):
        return LMXRegs(self)

    @property
    def f_pd(self):
        return self.OSC_R.f_out


    # REGISTER FIELDS
    @property
    def cal_clk_div(self):
        if self._best_lock:
            return 3
        
        if self.OSC_IN.f_out <= 200:
            return 0
        elif self.OSC_IN.f_out <= 400:
            return 1
        elif self.OSC_IN.f_out <= 800:
            return 2
        else:
            return 3

    @property
    def chdiv(self):
        return 0x0

    @property
    def cpg(self):
        return 0x7; ## IMPORTANT LOOK FOR UPDATES IN PYTHON

    @property
    def fcal_en(self):
        return self._fcal_en

    @fcal_en.setter
    def fcal_en(self, v):
        assert(v in [0, 1])
        self._fcal_en = v
        return v

    @property
    def fcal_hpfd_adj(self):
        if self.f_pd <= 100:
            return 0
        elif self.f_pd <= 150:
            return 1
        elif self.f_pd <= 200:
            return 2
        else:
            return 3

    @property
    def fcal_lpfd_adj(self):
        if self.f_pd >= 10:
            return 0
        elif self.f_pd >= 5:
            return 1
        elif self.f_pd >= 2.5:
            return 2
        else:
            return 3







    @property
    def inpin_fmt(self):
        return 0x0

    @property
    def inpin_hyst(self):
        return 0x0

    @property
    def inpin_ignore(self):
        return 0x1

    @property
    def inpin_lvl(self):
        return 0x1

    @property
    def jesd_dac1_ctrl(self):
        return 0x3f

    @property
    def jesd_dac2_ctrl(self):
        return 0x0

    @property
    def jesd_dac3_ctrl(self):
        return 0x0

    @property
    def jesd_dac4_ctrl(self):
        return 0x0

    @property
    def ld_dly(self):
        return 0x0
    
    @property
    def ld_type(self):
        return 0x1

    @property
    def mash_order(self):
        return 0x3

    @property
    def mash_reset_n(self):
        return 0x1

    @property
    def mash_rst_count(self):
        return 0xc350
    
    @property
    def mash_seed(self):
        return 0x0
    
    @property
    def mash_seed_en(self):
        return 0x0

    @property
    def mult(self):
        return self.OSCMult.mult

    @property
    def muxout_ld_sel(self):
        # wired to LED, so no readback
        return 1

    @property
    def osc_2x(self):
        return 1 if self.OSC2X.mult == 2 else 0

    @property
    def out_force(self):
        return 1
        
    @property
    def out_iset(self):
        return 0x0

    @property
    def out_mute(self):
        return 0

    @property
    def outa_mux(self):
        return self.AMUX.source

    @property
    def outa_pd(self):
        return 0x0

    @property
    def outa_pwr(self):
        return 0x1f

    @property
    def outb_mux(self):
        return self.BMUX.source

    @property
    def outb_pd(self):
        return 0x1
    
    @property
    def outb_pwr(self):
        return 0x1f

    @property
    def pfd_dly_sel(self):
        return 0x4

    @property
    def pll_den(self):
        return self.PLL.DEN

    @property
    def pll_n(self):
        return self.PLL.N

    @property
    def pll_num(self):
        return self.PLL.NUM
    
    @property
    def pll_r(self):
        return self.OSC_R.den

    @property
    def pll_r_pre(self):
        return self.PRE_R.den

    @property
    def powerdown(self):
        return 0;

    @property
    def quick_recal_en(self):
        return 0x0
    
    @property
    def ramp0_dly(self):
        return 0x0

    @property
    def ramp0_inc(self):
        return 0x800000

    @property
    def ramp0_len(self):
        return 0x0
    
    @property
    def ramp0_next(self):
        return 0x1
    
    @property
    def ramp0_next_trig(self):
        return 0x1
    
    @property
    def ramp0_rst(self):
        return 0x0
    
    @property
    def ramp1_dly(self):
        return 0x0

    
    @property
    def ramp1_inc(self):
        return 0x3f800000

    @property
    def ramp1_len(self):
        return 0x0
    
    @property
    def ramp1_next(self):
        return 0x0
    
    @property
    def ramp1_next_trig(self):
        return 0x1

    @property
    def ramp1_rst(self):
        return 0x0

    @property
    def ramp_burst_count(self):
        return 0x0

    @property
    def ramp_burst_en(self):
        return 0x0
    
    @property
    def ramp_burst_trig(self):
        return 0x0
    
    @property
    def ramp_dly_cnt(self):
        return 0x0

    @property
    def ramp_en(self):
        return 0

    @property
    def ramp_limit_high(self):
        return 0x1e000000

    @property
    def ramp_limit_low(self):
        return 0x1d3000000
    
    @property
    def ramp_manual(self):
        return 0x1

    @property
    def ramp_scale_cnt(self):
        return 0x0

    @property
    def ramp_thresh(self):
        return 0x266666
    
    @property
    def ramp_trig_cal(self):
        return 0x0

    @property
    def ramp_triga(self):
        return 0x1

    @property
    def ramp_trigb(self):
        return 0x1

    @property
    def rb_ld_vtune(self):
        return 0x0

    @property
    def rb_vco_capctrl(self):
        return 0x0

    @property
    def rb_vco_daciset(self):
        return 0x0
    
    @property
    def rb_vco_sel(self):
        return 0x0

    @property
    def reset(self):
        return self._reset

    @reset.setter
    def reset(self, v):
        assert(v in [0, 1])
        self._reset = v
        return v

    @property
    def seg1_en(self):
        return 0x1
    
    @property
    def sysref_div(self):
        return 0x1

    @property
    def sysref_div_pre(self):
        return 0x4

    @property
    def sysref_en(self):
        return 0x0

    @property
    def sysref_pulse(self):
        return 0x0

    @property
    def sysref_pulse_cnt(self):
        return 0x0
    
    @property
    def sysref_repeat(self):
        return 0x0
    
    @property
    def vco2x_en(self):
        return 1 if self.PLL2X.mult == 2 else 0

    @property
    def vco_capctrl(self):
        return self.VCO.cap_code

    @property
    def vco_capctrl_force(self):
        return 0

    @property
    def vco_capctrl_strt(self):
        return self.VCO.cap_code

    @property
    def vco_daciset(self):
        return self.VCO.amp_cal

    @property
    def vco_daciset_force(self):
        return 0

    @property
    def vco_daciset_strt(self):
        return self.VCO.amp_cal
        
    @property
    def vco_phase_sync(self):
        return 0

    @property
    def vco_sel(self):
        return self.VCO.vco_n
    
    @property
    def vco_sel_force(self):
        return 0x0




    



    

    @property
    def included_divide(self):
        if (self._VCO_PHASE_SYNC == 0 or
            self._SYSREF_EN == 0 and (
                (self.AMUX.source == 1 and self.BMUX.source == 1) or
                (self.AMUX.source == 2 and self.BMUX.source == 1))):
            return 1
        elif self._SEG1 % 3 == 0:
            return 6
        else:
            return 4
        
    @property
    def f_vco(self):
        return self.PLL.f_out

    @f_vco.setter
    def f_vco(self, f):
        r = f / self.OSC.f_out

        den = f / self.OSC_R.f_out

        i_den = math.floor(den)
        
        print(f"OSC: {self.OSC.f_out} f: {f} r: {r} den: {den}")

        self.PLL.N = i_den
        self.PLL.NUM = round(self.PLL.DEN*(den - i_den))

        print(f"PLL: N: {self.PLL.N} NUM: {self.PLL.NUM} DEN: {self.PLL.DEN}")

        print(f"VCO: AMP_CAL: {self.VCO.amp_cal} CAP_CODE: {self.VCO.cap_code} GAIN: {self.VCO.gain}")

    def tune(self, f):
        (A, B) = f
        VCOFreq = None
        c = copy.deepcopy(self)
        
        # One, find a VCO frequency that even works
        if A > 15000:
            if B > A / 2:
                raise Exception(f"B must be <= A/2 if doubler enabled: A: {A} B: {B}")
            # We need the doubler here
            c.AMUX.source = 2
            c.PLL2X.mult = 2
            VCOFreq = round(A / 2, 10)
        elif A >= 7500:
            if B > A:
                raise Exception(f"B must be <= A if A is raw VCO: A: {A} B: {B}")
            c.AMUX.source = 1
            c.PLL2X.mult = 1
            VCOFreq = round(A, 10)
        else:
            # Below lower limit of VCO            
            c.AMUX.source = 0
            c.PLL2X.mult = 1

            for i in self.PLLDIV.allowed:
                f = i * A

                if (f >= 7500 and (f <= 11500 or i <= 6)):
                    VCOFreq = round(f, 10)
                    print(f"{VCOFreq/B}")
                    c.PLLDIV.den = i
                    break

        if VCOFreq == None:
            raise Exception(f"Could not find proper VCO frequency for {A}MHz on port A");
            
        print(f"Selecting VCO frequency: {VCOFreq}")
        
        if B >= 7500:
            if B != VCOFreq:
                raise Exception(f"Could not match VCO for port B {B} VCO: {VCOFreq}")
            c.BMUX.source = 1
        else:
            if c.AMUX.source == 0 and A != B:
                raise Exception(f"A must equal B for divided frequencies")

            c.BMUX.source = 0
            den = VCOFreq / B
            rden = int(round(den, 1))
            if abs(den - rden) > 0.1:
                raise Exception(f"Unable to find integer divider for port B: {B} VCO: {VCOFreq} den: {den}")

            if abs(den - rden) > 0.001:
                print("WARNING: rounding B to {VCOFreq/rden}, requested {B}")
                B = VCOFreq/rden

            print(rden)
                
            c.PLLDIV.den = rden

            c.f_vco = VCOFreq
        
        
    @property
    def freqs(self):
        return (self.AMUX.f_out, self.BMUX.f_out)

    @freqs.setter
    def freqs(self, f):
        self.tune(f)

    def display(self):
        print(f"Input Freq: {self.OSC.freq} 2X: {self.OSC2X.f_out} Pre-R: {self.PRE_R.f_out} Mult: {self.OSCMult.f_out} Post-R: {self.OSC_R.f_out}")
        print(f"VCO: {self.VCO.vco_n} freq: {self.VCO.f_out}")
        print(f"AMUX: {self.AMUX.f_out}")
        print(f"BMUX: {self.BMUX.f_out}")
