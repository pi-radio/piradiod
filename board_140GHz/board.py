import os
import time

from picommand import PiCommandObject, picommand
from pioutput import pioutput
from spidev import SPIDev
from LTC5584 import LTC5584Dev
from LMX2595 import LMX2595Dev
from MAX11300 import MAX11300Dev

class HCPort(PiCommandObject):
    def __init__(self, chip, ports, maxV):
        self.chip = chip
        self._V = 0.0
        self.maxV = maxV
        self.Rsense = 0.1

        self.dac = chip.port[ports[0]]
        self.adcp = chip.port[ports[1]]
        self.adcn = chip.port[ports[2]]
        
        self.ports = ports

        self.adcn.begin_config()
        self.adcp.begin_config()
        self.dac.begin_config()
        
        self.dac.range = 6
        self.dac.dac = self._V 
        
        self.adcn.avr = 0
        self.adcn.range = 6
        
        self.adcp.assoc_port = ports[2]
        self.adcp.avr = 0
        self.adcp.range = 6
        
        self.dac.funcid = self.chip.FUNCID_DAC_MONITOR
        self.adcp.funcid = self.chip.FUNCID_DADCP
        self.adcn.funcid = self.chip.FUNCID_DADCN
        
        self.adcn.end_config()
        time.sleep(0.001)
        self.adcp.end_config()
        time.sleep(0.001)
        self.dac.end_config()
        time.sleep(0.001)

    @property
    def V(self):
        return self._V

    @V.setter
    def V(self, V):
        assert(V <= self.maxV)
        self._V = V
        self.dac.dac = self._V
        return self._V

    @property
    def I(self):
        return self.adcp.adc / self.Rsense

    @property
    def V_sense_lo(self):
        return self.adcn.adc / self.Rsense
    
    def ramp_to(self, V):
        assert(V <= self.maxV)
        N = 16
        delay = 0.01
        dV = (V - self.V) / N

        for i in range(N - 1):
            self.V += dV
            time.sleep(delay)
            pioutput.print(f"V: {self.V} {self.V_sense_lo} Current: {self.I}")
            
        self.V = V

#
#    Left
#
# -- InP_Vbb_Common (0-2)
# -- Mixer Vcm Left (3)
# -- Mixer VLO Left (4-6)
# -- x9 Vdd Left (7-9)
# -- PA Vdd (10-12)
# -- Bias Vdd Left (13)
# -- x9 Vgs Left (14)
# -- PA_Vgs_Left (15)
#
#    Right
#
# -- InP_Vcc_Common (0-2)
# -- Mixer_VCM_Right (3)
# -- Mixer_VLO_Right (4-6)
# -- x9_VDD_Right (7-9)
# -- PA_VDD_Right (10-12)
# -- Bias VDD Right 13
# -- x9 Vgs Right (14)
# -- PA_Vgs_Right (15)


class InP_PA(PiCommandObject):
    def __init__(self, mod):
        self.mod = mod

    def up(self):
        pass

    def down(self):
        pass

        
class PA(PiCommandObject):
    def __init__(self, mod):
        self.mod = mod

    def up(self):
        pass

    def down(self):
        pass



class Side(PiCommandObject):
    def __init__(self, side):
        print(f"SIDE: {side.device_ctrl:4x}")
        
        self.children.VDD = HCPort(side, (7, 8, 9), maxV=0.83)
        self.children.VGS = side.port[13]

        self.children.VGS.range = 6
        self.children.VGS.funcid = side.FUNCID_DAC
        
    @picommand
    def up(self):
        pioutput.print(f"X9 -- Bringing up {self}")
        self.children.VDD.ramp_to(0.8)
        # check current

        self.children.VGS.ramp_to(0.55)
            
        pioutput.print(f"X9 VDD Current: {self.children.VDD.I}")

    @picommand
    def watch(self):
        while True:
            print(f"DAC MONITOR: {self.children.VDD.dac.adc}")
            print(f"ADCP: {self.children.VDD.adcp.adc}")
            print(f"ADCN: {self.children.VDD.adcn.adc}")
            time.sleep(1)
        
class X9(PiCommandObject):
    def __init__(self, mod):
        self.mod = mod
        self.children.L = Side(self.mod.pwr_l)
        self.children.R = Side(self.mod.pwr_r)

    def up(self):
        pioutput.print("X9 going up!")
        self.children.L.up()
        self.children.R.up()


    def down(self):
        pioutput.print("X9 going down!")
        self.children.R.down()
        self.children.L.down()
        
        
        
class Mixer(PiCommandObject):
    def __init__(self, mod):
        self.mod = mod

    def up(self):
        pass

    def down(self):
        pass

class RXModule(PiCommandObject):
    def __init__(self):
        self.pwr_l = MAX11300Dev(2, 8)
        self.pwr_r = MAX11300Dev(2, 9)

        self.pwr_l.setup()
        self.pwr_r.setup()

        
        self.children.PA = PA(self)
        self.children.x9 = X9(self)
        self.children.mixer = Mixer(self)

        
    @picommand
    def up(self):
        pass

    @picommand
    def down(self):
        pass


class TXModule(PiCommandObject):
    def __init__(self):
        self.pwr_l = MAX11300Dev(2, 10)
        self.pwr_r = MAX11300Dev(2, 11)

        self.pwr_l.setup()
        self.pwr_r.setup()
        
        self.children.InP = InP_PA(self)
        
        self.children.PA = PA(self)
        self.children.x9 = X9(self)
        self.children.mixer = Mixer(self)
        
    @picommand
    def up(self):
        self.children.InP.up()
        self.children.PA.up()
        self.children.mixer.up()
        self.children.x9.up()

    @picommand
    def down(self):
        self.children.x9.down()
        self.children.mixer.down()
        self.children.PA.down()
        self.children.InP.down()

    
class PiRadio_140GHz_Bringup(PiCommandObject):
    def __init__(self):
        print("Initializing 140GHz Bringup Board")

        self.children.LTC5584 = [ LTC5584Dev(2, i) for i in range(8) ]

        self.children.TX = TXModule()
        self.children.RX = RXModule()
        
        self.children.LMX_Eravant = LMX2595Dev(2, 12)
        self.children.LMX_RX = LMX2595Dev(2, 13)
        self.children.LMX_TX = LMX2595Dev(2, 14)

    @picommand
    def hello(self):
        print("hello")

    @picommand
    def load(self):
        os.system("modprobe spidev")

        p = os.path.dirname(os.path.abspath(__file__))
        
        os.system("fpgautil -b {p}/system.bin -m {p}/system.dtbo")
