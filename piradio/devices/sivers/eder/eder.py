from piradio.output import output
from piradio.command import CommandObject, command
from piradio.devices.sivers.eder.registers import attach_registers, set_bits, clear_bits
from piradio.devices.sivers.eder.adc import ADC
from piradio.devices.sivers.eder.eeprom import EEPROM
from piradio.devices.sivers.eder.rx import RX



class FreqRef:
    def __init__(self, eder):
        self.eder = eder

        self.freq = 45e6

    def startup(self):
       self.eder.bias_ctrl = set_bits(0x1c)
       self.eder.bias_pll = set_bits(0x07)
       self.eder.pll_en = set_bits(0x08)

       self.eder.fast_clk_ctrl = 0x20
       self.eder.pll_ref_in_lvds_en = 0x1

       output.info(f"SIVERS: Ref Clk {self.freq:.2f} MHz")

    # Write monitor enable/disable

    @property
    def dig_freq(self):
        if self.eder.fast_clk_ctrl & 0x10:
            return self.freq * 5
        else:
            return self.freq * 4

    def dig_cycles(self, us):
        return round(us * self.dig_freq / 1e6)
    
class Eder: #(CommandObject):
    def __init__(self, spi, i2c=None):
        self.spi = spi

        self.eeprom = EEPROM(i2c)
        
        attach_registers(self)

        print("DOOKIE!")

        self.cid = self.regs.chip_id

        if self.cid == 0x02731803:
            print("Found Eder B")
        elif self.cid == 0x02741812:
            print("Found Eder B MMF")
        else:
            raise RuntimeError("Unknown SIVERS chip")

    def startup(self):
        self.ref = FreqRef(self)

        self.adc = ADC(self)

        self.ref.startup()

        self.adc.startup()

        self.eeprom.startup()

        
