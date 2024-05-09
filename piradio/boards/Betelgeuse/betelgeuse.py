import glob
import time
from pathlib import Path
from piradio.devices import SysFS, SPIDev, AXI_GPIO, StreamFIR

class Betelgeuse:
    connector_names = [ f"JRF{i+1}" for i in range(8) ]

    class Port:
        def __init__(self, board, n, connector, pwren, spi, adc, dac):
            self.board = board
            self.connector = connector
            self.pwren = pwren
            self.spi = spi
            self.adc = adc
            self.dac = dac
            self.n = n

        def set_adc_gain(self, gain):
            self.board.set_amp_gain(self.spi, 0, gain)

        def set_dac1_gain(self, gain):
            self.board.set_amp_gain(self.spi, 1, gain)

        def set_dac2_gain(self, gain):
            self.board.set_amp_gain(self.spi, 2, gain)

            
    def __init__(self, reinit=True):
        self._ports = [
            self.Port(self, 0, connector='JRF1', pwren=7, spi=1, adc=4, dac=1),
            self.Port(self, 1, connector='JRF2', pwren=5, spi=0, adc=7, dac=0),
            self.Port(self, 2, connector='JRF3', pwren=3, spi=4, adc=3, dac=4),
            self.Port(self, 3, connector='JRF4', pwren=1, spi=5, adc=0, dac=5),
            self.Port(self, 4, connector='JRF5', pwren=6, spi=3, adc=6, dac=3),
            self.Port(self, 5, connector='JRF6', pwren=4, spi=2, adc=5, dac=2),
            self.Port(self, 6, connector='JRF7', pwren=2, spi=6, adc=1, dac=6),
            self.Port(self, 7, connector='JRF8', pwren=0, spi=7, adc=2, dac=7)
        ]

        try:
            self.output_filters = [ StreamFIR(f"data_capture_filter_out{i}") for i in range(8) ]
        except:
            self.output_filters = [ StreamFIR(f"filter_out{i}") for i in range(8) ]
        
        l = glob.glob("/sys/firmware/devicetree/base/__symbols__/*pl_gpio")

        assert len(l) == 1, "Too many GPIO units found: {l}"

        gpio = Path(l[0]).name
        
        self.gpios = AXI_GPIO(gpio)

        self.power_enable = self.gpios.outputs[0]
        self.programn = self.gpios.outputs[1]
        self.jtagen = self.gpios.outputs[2]

        self.ampchsel = [ self.gpios.outputs[i] for i in range(3, 11) ]
        self.ampcs =  [ self.gpios.outputs[i] for i in range(11, 14) ]

        self.pwren = [ self.gpios.outputs[i] for i in range(14, 22) ]

        self.rfdcrst = self.gpios.outputs[26]
        self.rfdcrstn = self.gpios.inputs[41]
        
        self.initn = self.gpios.inputs[32]
        self.done = self.gpios.inputs[33]

        self.ctrl_spi = SPIDev.find_spi_device("CTRL0")
        self.amps_spi = SPIDev.find_spi_device("AMPS0")

        if reinit:
            self.startup()

    @property
    def ports(self):
        return self._ports
        
    def startup(self):
        print("Resetting and starting up Betelguese RF board...")
        self.power_enable.val = 0
        self.rfdcrst.val = 1
        
        for chsel in self.ampchsel:
            chsel.val = 0

        for cs in self.ampcs:
            cs.val = 1
        
        for pwren in self.pwren:
            pwren.val = 0

        self.programn.val = 1
        self.jtagen.val = 1
        time.sleep(0.5)
        self.power_enable.val = 1
        self.rfdcrst.val = 0

        time.sleep(0.1)
        
        for pwren in self.pwren:
            pwren.val = 1
        
    def dump_lattice_status(self):
        print(f"PROGRAMN: {self.programn.val} JTAGEN: {self.jtagen.val} INITN: {self.initn.val} DONE: {self.done.val}")

    def select_amp(self, channel, cs):
        self.ampchsel[channel].val = 1
        self.ampcs[cs].val = 0
        
    def deselect_amp(self, channel, cs):
        self.ampchsel[channel].val = 0
        self.ampcs[cs].val = 1
        
    def read_amp_reg(self, channel, cs, reg):
        self.select_amp(channel, cs)
        
        data = self.amps_spi.xfer([0x80 | reg, 0x00])

        self.deselect_amp(channel, cs)
        
        return data[1]

    def set_amp_reg(self, spi_channel, cs, reg, val):
        self.select_amp(spi_channel, cs)
        
        data = self.amps_spi.xfer([reg, val])

        self.deselect_amp(spi_channel, cs)
        
        return data[1]

    def reset_gains(self):
        for channel in range(len(self.ampchsel)):
            for cs in range(len(self.ampcs)):
                self.set_amp_gain(channel, cs, -6)
    
    def set_amp_gain(self, spi_channel, cs, gain):
        assert gain >= -6 and gain <= 26, f"Invalid gain {gain}"
        rval = int(32 - (gain - -6))
        return self.set_amp_reg(spi_channel, cs, 2, rval)
        
    def dump_regs(self):
        for channel in range(len(self.ampchsel)):
            print(f"Channel: {channel}")
            
            for cs in range(len(self.ampcs)):
                print(f" CS: {cs}")
                
                for reg in range(6):
                    print(f"  Reg: {reg} Val: {self.read_amp_reg(channel, cs, reg):2x}")
