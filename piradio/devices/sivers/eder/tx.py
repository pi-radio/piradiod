from piradio.devices.sivers.eder.registers import attach_registers, set_bits, clear_bits, modify_bits
from .beamforming import Beamformer
from .BFM06010 import TXWeights

class TX(Beamformer):
    def __init__(self, eder):
        super().__init__(eder, TXWeights)
        self._freq = 0
        self._omni = True

    def startup(self):
        self.eder.regs.trx_tx_on = 0x1FFFFF

        if self.eder.mmf:
            self.eder.regs.bias_tx = 0x96AA
        else:
            self.eder.regs.bias_tx = 0xAEAA

        self.regs.bias_ctrl = set_bits(0x7F)
        self.regs.bias_lo = set_bits(0xA)

        self.regs.tx_ctrl = 0x18
        self.regs.tx_bb_gain = 0x00
        self.regs.tx_bb_phase = 0x00
        self.regs.tx_bb_iq_gain = 0xFF
        self.regs.tx_bfrf_gain = 0x77
        
        print("TX startup complete")
        self.azimuth = 0.0
        self.update_beamformer()
            

    def ready(self):
        pass
        
    @property
    def beamweights_reg(self):
        return self.regs.bf_tx_awv

    
