import gc
import time

from piradio.output import output
from piradio.command import StateMachine, command, cmdproperty, State, transition, precondition
from piradio.devices.sivers.eder.registers import attach_registers, set_bits, clear_bits, toggle_bits, modify_bits
from piradio.devices.sivers.eder.adc import ADC
from piradio.devices.sivers.eder.eeprom import EEPROM
from piradio.devices.sivers.eder.rx import RX
from piradio.devices.sivers.eder.tx import TX
from piradio.devices.sivers.eder.selftest import self_test, agc_test
from piradio.devices.sivers.eder.tasks import register_eder
from piradio.devices.sivers.eder.pll import FreqRef, PLL

def KtoC(K):
    return K - 273.15

class Eder(StateMachine):
    CID_EDER_B = 0x02731803
    CID_EDER_B_MMF = 0x02741812

    PRERESET = State("pre-reset", initial=True)
    RESET = State("reset")
    INIT = State("initialized")
    SX = State("SX")
    HWCTRL = State("HWCTRL")
    RX = State("RX")
    TX = State("TX")
    
    def __init__(self, spi, i2c=None):
        super().__init__()
        self.spi = spi

        self.eeprom = EEPROM(i2c)
        
        attach_registers(self)

        self.cid = self.regs.chip_id

        if self.cid == self.CID_EDER_B:
            output.info("Found Eder B")
        elif self.cid == self.CID_EDER_B_MMF:
            output.info("Found Eder B MMF")
        else:
            raise RuntimeError("Unknown SIVERS chip")

        self.ref = FreqRef(self)
        self.pll = PLL(self)
        self.adc = ADC(self)
        self.rx = RX(self)
        self.tx = TX(self)

    def __del__(self):
        self.regs.trx_ctrl = clear_bits(0xB)
        
    def __setattr__(self, name, value):
        if hasattr(self, "regs") and name in self.regs.registers:
            raise RuntimeError("Attempt to assign to variable with reg name on object")

        return super().__setattr__(name, value)

    @cmdproperty
    def freq(self):
        return self.pll.freq

    @freq.setter
    def freq(self, v : float):
        if self.cur_state == None or self.cur_state == self.PRERESET or self.cur_state == self.RESET:
            self.INIT()
            
        self.pll.freq = v
        self.rx.freq = v
        self.tx.freq = v
        

    @cmdproperty
    def Tj(self):
        return self.adc.tj
        
    @property
    def mmf(self):
        return self.cid == self.CID_EDER_B_MMF

    @command
    @transition(PRERESET, RESET)
    def reset(self):
        self.regs.vco_tune_ctrl = set_bits(0xFF)
        self.regs.vco_tune_ctrl = clear_bits(0xFF)

        self.adc.reset()
        self.pll.reset()
        
    @command
    @transition(RESET, INIT)
    def startup(self, run_tests=False):        
        self.ref.startup()

        self.adc.startup()

        self.eeprom.startup()

        self.pll.startup()

        prevT = 0.0
        curT = self.adc.tj

        output.info("Waiting for stable temperature")
        
        while abs(curT - prevT) > 0.1:
            prevT = curT
            time.sleep(1)
            curT = self.adc.tj
            output.info(f"Temp: {KtoC(curT)} C")

        self.rx.startup()
        self.tx.startup()
        
        register_eder(self)
            
        output.info("Eder initialized")
        
    @command
    @transition(INIT, SX)
    @precondition(lambda obj: obj.freq != 0.0)
    def init_to_SX(self):
        self.rx.ready()
        self.tx.ready()

    @command
    @transition(SX, HWCTRL)
    def SX_to_HWCTRL(self):
        self.regs.trx_ctrl = set_bits(8)

    @command
    @transition(HWCTRL, SX)
    def HWCTRL_to_SX(self):
        self.regs.trx_ctrl = clear_bits(8)
        
    @command
    @transition(SX, RX)
    def SX_to_RX(self):
        self.regs.trx_ctrl = set_bits(1)

    @command
    @transition(RX, SX)
    def RX_to_SX(self):
        self.regs.trx_ctrl = clear_bits(1)
        

    @command
    @transition(SX, TX)
    def SX_to_TX(self):
        self.regs.trx_ctrl = set_bits(2)

    @command
    @transition(TX, SX)
    def TX_to_SX(self):
        self.regs.trx_ctrl = clear_bits(2)

        
    def bringup_tests(self):
        self_test(eder)
        agc_test(eder)


    
        
