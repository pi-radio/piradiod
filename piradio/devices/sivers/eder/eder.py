import gc
import time

from piradio.output import output
from piradio.command import StateMachine, command, cmdproperty, State, transition, precondition, TaskGroup
from piradio.devices.sivers.eder.registers import attach_registers, set_bits, clear_bits, toggle_bits, modify_bits
from piradio.devices.sivers.eder.adc import ADC
from piradio.devices.sivers.eder.eeprom import EEPROM
from piradio.devices.sivers.eder.rx import RX
from piradio.devices.sivers.eder.tx import TX
from piradio.devices.sivers.eder.selftest import self_test, agc_test
from piradio.devices.sivers.eder.pll import FreqRef, PLL
from piradio.devices.sivers.eder.config import EderConfig



def KtoC(K):
    return K - 273.15

class EderChipNotFoundError(RuntimeError):
    pass

class Eder(StateMachine):

    PRERESET = State("pre-reset", initial=True)
    RESET = State("reset")
    INIT = State("initialized")
    SX = State("SX")
    HWCTRL = State("HWCTRL")
    RX = State("RX")
    TX = State("TX")
    LOOP = State("LOOP")
    
    def __init__(self, spi, N, i2c=None):
        super().__init__()
        self.task_group = TaskGroup()
        self.N = N
        self.spi = spi
        
        self.eeprom = EEPROM(i2c)
        
        attach_registers(self)

        self.cid = self.regs.chip_id

        if not self.is_eder_b and not self.is_eder_b_mmf:
            self.spi = None
            raise EderChipNotFoundError(f"Unknown SIVERS chip {self.cid}")

        self._config = EderConfig(self)

        self.ref = FreqRef(self)
        self.pll = PLL(self)
        self.adc = ADC(self)
        self.rx = RX(self)
        self.tx = TX(self)

    def __del__(self):
        self._config.save()
    
    @property
    def config(self):
        return self._config
        
    @property
    def is_eder_b(self):
        return self.cid == 0x02731803

    @property
    def is_eder_b_mmf(self):
        return self.cid == 0x02741812

    @property
    def mmf(self):
        return self.is_eder_b_mmf
    
    def __del__(self):
        if self.spi is not None:
            self.SX()
            self.regs.trx_ctrl = clear_bits(0x3)
        
    def __setattr__(self, name, value):
        if "regs" in self.__dict__ and name in self.regs.registers:
            raise RuntimeError("Attempt to assign to variable with reg name on object")

        return super().__setattr__(name, value)

    @cmdproperty
    def freq(self):
        return self.pll.freq

    @freq.setter
    def freq(self, v : float):
        assert v >= 55e9 and v <= 70e9
        
        if self.cur_state == None or self.cur_state == self.PRERESET or self.cur_state == self.RESET:
            self.INIT()
            
        self.pll.freq = v
        self.rx.load_weights()
        self.tx.load_weights()

    def steer(self, angle : float):
        if self.cur_state == self.TX:
            self.tx.azimuth = angle
        elif self.cur_state == self.RX:
            self.rx.azimuth = angle
        else:
            output.warn(f"Not in mode to steer {self.cur_state}")
            
    def omni(self):
        if self.cur_state == self.TX:
            self.tx.omni = True
        elif self.cur_state == self.RX:
            self.rx.omni = True
        else:
            output.warn(f"Not in mode to steer {self.cur_state}")

    def tx_status(self):
        self.tx.pdet_dump()

    @property
    def Tj(self):
        return KtoC(self.adc.tj)
        
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
        curT = self.Tj

        output.debug("Waiting for stable temperature")
        
        while abs(curT - prevT) > 0.1:
            prevT = curT
            time.sleep(1)
            curT = self.Tj

        self.task_group.create_task(5, self.monitor)
            
        try:
            self.rx.startup()
            self.tx.startup()
        except RuntimeError as e:
            output.warn("Intialization failed")
            self.regs.trx_ctrl = 0
            return

        print(f"Radio {self.N} initialized")
        output.debug("Eder initialized")
        
    @transition(INIT, SX)
    @precondition(lambda obj: obj.freq != 0.0)
    def init_to_SX(self):
        self.rx.ready()
        self.tx.ready()

    @transition(SX, HWCTRL)
    def SX_to_HWCTRL(self):
        self.regs.trx_ctrl = set_bits(8)

    @transition(HWCTRL, SX)
    def HWCTRL_to_SX(self):
        self.regs.trx_ctrl = clear_bits(8)

    @transition(SX, LOOP)
    def SX_to_LOOP(self):
        self.rx.loopback()
        self.tx.loopback()
        self.regs.trx_ctrl = set_bits(3)
        
    @transition(LOOP, SX)
    def LOOP_to_SX(self):
        self.regs.trx_ctrl = clear_bits(3)
        self.rx.loopback_off()
        self.tx.loopback_off()
        
    @transition(SX, RX)
    def SX_to_RX(self):
        self.regs.trx_ctrl = set_bits(1)
        self.rx.enable()

    @transition(RX, SX)
    def RX_to_SX(self):
        self.regs.trx_ctrl = clear_bits(1)
        self.rx.disable()
        

    @transition(SX, TX)
    def SX_to_TX(self):
        print("TX MF!")
        self.regs.trx_ctrl = set_bits(2)

    @transition(TX, SX)
    def TX_to_SX(self):
        print("Leaving TX")
        self.regs.trx_ctrl = clear_bits(2)

    def get_tx_pwr(self):
        print(" ".join([f"{i:03x}" for i in self.adc.tx_pdet]))
        print(" ".join([f"{i}" for i in self.adc.tx_pdet]))
        print(" ".join([f"{i:03x}" for i in self.adc.tx_env_pdet]))
        print(" ".join([f"{i}" for i in self.adc.tx_env_pdet]))
        
    def monitor(self):
        if self.Tj > 85:
            print(f"Overtemp event on radio {self.N}: {self.Tj:.1f} C")
            self.SX()
                    
    def bringup_tests(self):
        self_test(eder)
        agc_test(eder)

    def post_transition(self, start, end):
        print(f"Transition: {start}=>{end}")
        print(f"trx_ctrl: {self.regs.trx_ctrl}")
        print(f"tx_ctrl: {self.regs.tx_ctrl}")
        
    
        
