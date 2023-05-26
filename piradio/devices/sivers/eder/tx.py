from piradio.output import output
from piradio.devices.sivers.eder.registers import attach_registers, set_bits, clear_bits, modify_bits
from .beamforming import Beamformer
from .BFM06010 import TXWeights

class TX(Beamformer):
    def __init__(self, eder):
        super().__init__(eder, TXWeights)
        self._omni = True

    def startup(self):
        self.eder.regs.trx_tx_on = 0x1FFFFF
        self.eder.regs.trx_tx_off = 0x000000

        if self.eder.mmf:
            self.eder.regs.bias_tx = 0x96AA
        else:
            self.eder.regs.bias_tx = 0xAEAA

        self.regs.bias_ctrl = set_bits(0x40)
        self.regs.bias_lo = set_bits(0xA)

        self.regs.tx_ctrl = 0x08
        self.regs.tx_bb_gain = 0x00
        self.regs.tx_bb_phase = 0x00
        self.regs.tx_bb_iq_gain = 0xFF
        self.regs.tx_bfrf_gain = 0xFF

        self.regs.tx_bb_q_dco = 0x00
        self.regs.tx_bb_i_dco = 0x00
        
        print("TX startup complete")
        self.omni = True
        self.update_beamformer()


    def alc_init(self):
        self.regs.tx_alc_pdet_lo_th = 0x80
        self.regs.tx_alc_pdet_hi_offs_th = 0x04
        self.regs.tx_alc_ctrl = alc_ctrl
        self.regs.tx_alc_loop_cnt = 0x00
        self.regs.tx_alc_start_delay = self.dig_pll.cycles(2)   # 2 us
        self.regs.tx_alc_meas_delay = self.dig_pll.cycles(1)   # 1 us
        self.regs.tx_alc_bfrf_gain_max = 0xff
        self.regs.tx_alc_bfrf_gain_min = 0x00
        self.regs.tx_alc_step_max = 0x13
        self.regs.tx_bf_pdet_mux = set_bits(0x80)


    def alc_enable(self):
        self.regs.tx_alc_ctrl = set_bits(0x01)

    def alc_disable(self):
        self.regs.tx_alc_ctrl = clear_bits(0x03)


    def alc_start(self):
        if (self.regs.tx_alc_ctrl & 0x01) == 0x01:
            self.regs.tx_alc_ctrl = toggle_bits(0x02)
        else:
            self.regs.tx_alc_ctrl = clear_bits(0x03)
            self.regs.tx_alc_ctrl = set_bits(0x03)

    def alc_stop(self):
        if (self.regs.tx_alc_ctrl & 0x01) == 0x01:
            self.regs.tx_alc_ctrl = clear_bits(0x03)
            self.regs.tx_alc_ctrl = set_bits(0x01)
        else:
            self.regs.tx_alc_ctrl = clear_bits(0x03)

    def pdet_dump(self):
        #bist_amux_ctrl = self.regs.bist_amux_ctrl
        #tx_bf_pdet_mux = self.regs.tx_bf_pdet_mux

        adc = self.eder.adc
        
        output.print("Detector power:")
        
        def get_pdet(i):
            return (i, adc.acquire(adc.pdet[i]).mean, adc.acquire(adc.env_pdet[i]).mean)
        
        pdet_vals = [ get_pdet(i) for i in range(0, 16) ]

        for i, power, env_power in pdet_vals:
            output.print(f"{i}: {power} {env_power}")

            
    def ready(self):
        pass

    def loopback(self):
        self.regs.tx_ctrl = set_bits(0x40)
        self.regs.trx_ctrl = set_bits(0x03)

    def loopback_off(self):
        self.regs.tx_ctrl = clear_bits(0x40)
        self.regs.trx_ctrl = clear_bits(0x03)

        
    @property
    def beamweights_reg(self):
        return self.regs.bf_tx_awv

    @property
    def bf_idx_reg(self):
        return self.regs.bf_tx_awv_ptr

    @bf_idx_reg.setter
    def bf_idx_reg(self, v):
        self.regs.bf_tx_awv_ptr = v
    

    
