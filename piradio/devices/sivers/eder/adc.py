from piradio.output import output
from .registers import set_bits, clear_bits, modify_bits

class ADCMux:
    bg_pll       = 0
    bg_tx        = 1
    bg_rx        = 2
    temp         = 3
    rx_bb        = 4
    vco          = 5
    vcc_pll      = 6
    tx_pdet      = 7
    adc_ref      = 8
    dco_i        = 9
    dco_q        = 10
    dco_cm       = 11
    otp          = 12
    tx_env_pdet  = 13
    vcc_pa       = 14
    vcc_tx       = 15

    def __get__(self, obj, objtype=None):
        return obj.eder.bist_amux_ctrl & 0x7F

    def __set__(self, obj, val):
        obj.eder.bist_amux_ctrl = val

class RXBBMux:
    rx_bb_mix_pd_i    = 1
    rx_bb_mix_pd_q    = 2
    rx_bb_mix_pd_th_i = 5
    rx_bb_mix_pd_th_q = 6
    rx_bb_mix_dc_p_i  = 9
    rx_bb_mix_dc_p_q  = 10
    rx_bb_mix_dc_n_i  = 13
    rx_bb_mix_dc_n_q  = 14
    rx_bb_inb_pd_i    = 17
    rx_bb_inb_pd_q    = 18
    rx_bb_inb_pd_th_i = 21
    rx_bb_inb_pd_th_q = 22
    rx_bb_inb_dc_p_i  = 25
    rx_bb_inb_dc_p_q  = 26
    rx_bb_inb_dc_n_i  = 29
    rx_bb_inb_dc_n_q  = 30
    rx_bb_vga1_pd_i    = 33
    rx_bb_vga1_pd_q    = 34
    rx_bb_vga1_pd_th_i = 37
    rx_bb_vga1_pd_th_q = 38
    rx_bb_vga1_dc_p_i  = 41
    rx_bb_vga1_dc_p_q  = 42
    rx_bb_vga1_dc_n_i  = 45
    rx_bb_vga1_dc_n_q  = 46
    rx_bb_vga2_pd_i    = 49
    rx_bb_vga2_pd_q    = 50
    rx_bb_vga2_pd_th_i = 53
    rx_bb_vga2_pd_th_q = 54
    rx_bb_vga2_dc_p_i  = 57
    rx_bb_vga2_dc_p_q  = 58
    rx_bb_vga2_dc_n_i  = 61
    rx_bb_vga2_dc_n_q  = 62
    rx_bb_vga1db_pd_i    = 65
    rx_bb_vga1db_pd_q    = 66
    rx_bb_vga1db_pd_th_i = 69
    rx_bb_vga1db_pd_th_q = 70
    rx_bb_vga1db_dc_p_i  = 73
    rx_bb_vga1db_dc_p_q  = 74
    rx_bb_vga1db_dc_n_i  = 77
    rx_bb_vga1db_dc_n_q  = 78
    rx_bb_outb_pd_i    = 81
    rx_bb_outb_pd_q    = 82
    rx_bb_outb_pd_th_i = 85
    rx_bb_outb_pd_th_q = 86
    rx_bb_outb_dc_p_i  = 89
    rx_bb_outb_dc_p_q  = 90
    rx_bb_outb_dc_n_i  = 93
    rx_bb_outb_dc_n_q  = 94
    
    def __get__(self, obj, objtype=None):
        return obj.eder.rx_bb_test_ctrl & 0x7F

    def __set__(self, obj, val):
        obj.eder.bist_amux_ctrl = obj.amux.amux_rx_bb
        obj.eder.rx_bb_test_ctrl = val

class VCOMux:
    vco_alc_th    = 0
    vco_vco_amp   = 1
    vco_atc_lo_th = 2
    vco_atc_hi_th = 3
    vco_vcc_vco   = 4
    vco_vcc_chp   = 5
    vco_vcc_synth = 6
    vco_vcc_bb_tx = 7
    vco_vcc_bb_rx = 8

    def __get__(self, obj, objtype=None):
        return obj.eder.vco_amux_ctrl & 0x7F

    def __set__(self, obj, val):
        obj.eder.bist_amux_ctrl = obj.amux.amux_vco
        obj.eder.vco_amux_ctrl = val

    
class TempMux:
    otp_temp_th   = 0
    otp_vdd_1v2   = 1
    otp_vdd_1v8   = 2
    otp_vcc_rx    = 3

    def __get__(self, obj, objtype=None):
        return obj.eder.vco_ot_ctrl & 0x7F

    def __set__(self, obj, val):
        obj.eder.bist_amux_ctrl = obj.amux.amux_otp
        obj.eder.vco_ot_ctrl = val
    
class LDMux:
    pll_ld_ld     = 0
    pll_ld_xor    = 1
    pll_ld_ref    = 2
    pll_ld_vco    = 3
    pll_ld_ld_raw = 4
    pll_ld_tst_0  = 5
    pll_ld_tst_1  = 6

class PDETMux:
    pdet          = (0 << 4)
    alc_lo_th     = (1 << 4)
    alc_hi_th     = (2 << 4)
    dig_pll_vtune = (3 << 4)

    def __get__(self, obj, objtype=None):
        return obj.eder.tx_bf_pdet_mux & 0x7F

    def __set__(self, obj, val):
        obj.eder.bist_amux_ctrl = obj.amux.amux_tx_pdet
        obj.eder.tx_bf_pdet_mux = val
    
class EnvPDETMux:
    pdet          = (0 << 4)
    alc_lo_th     = (1 << 4)
    alc_hi_th     = (2 << 4)
    dig_pll_vtune = (3 << 4)

    def __get__(self, obj, objtype=None):
        return obj.eder.tx_bf_pdet_mux & 0x7F

    def __set__(self, obj, val):
        obj.eder.bist_amux_ctrl = obj.amux.amux_tx_env_pdet
        obj.eder.tx_bf_pdet_mux = val

    
class ADC:
    amux = ADCMux()
    rx_bb = RXBBMux()
    vco = VCOMux()
    temp = TempMux()
    ld = LDMux()
    pdet = PDETMux()
    env_pdet = EnvPDETMux()

    adc_sample_clk = 19e6
    sample_cycle = 10
    
    def __init__(self, eder):
        self.eder = eder

    def enable(self):
        self.eder.bist_amux_ctrl = set_bits(0x80)

    def disable(self):
        self.eder.bist_amux_ctrl = clear_bits(0x80)

    def startup(self):
        self.eder.bias_ctrl = set_bits(0x60)

        div = int(((38 * self.adc_sample_clk) / self.eder.ref.dig_freq) - 1)

        self.eder.adc_clk_div = div
        self.eder.adc_sample_cycle = self.sample_cycle
        self.edge = 0

        output.info("SIVERS: ADC initialized")
        
    @property
    def edge(self):
        return (self.eder.adc_ctrl >> 1) & 1

    @edge.setter
    def edge(self, b):
        self.eder.adc_ctrl = modify_bits(b, 2)

    @property
    def mean(self):
        return self.eder.adc_mean & 0xfff

    @property
    def max(self):
        return self.eder.adc_max & 0xfff

    @property
    def min(self):
        return self.eder.adc_min & 0xfff

    @property
    def diff(self):
        return self.eder.adc_diff & 0xfff
