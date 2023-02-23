import os
import time

from piradio.command import CommandObject, command, cmdproperty
from piradio.output import output
from piradio.devices import SPIDev
from piradio.devices import LTC5584Dev
from piradio.devices import LMX2595Dev
from piradio.devices import MAX11300Dev
from piradio.devices import SampleBufferIn, SampleBufferOut
from piradio.zcu111 import zcu111

from piradio.util import GHz, MHz, Hz

from .rx import RX
from .tx import TX

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


        
    
class UCSB(CommandObject):
    mult_eravant = 12
    mult_UCSB = 9

    def __init__(self):
        print("Initializing 140GHz Bringup Board")

        self.children.LTC5584 = [ LTC5584Dev(2, i) for i in range(8) ]
        self.children.input_samples = [ SampleBufferIn(i) for i in range(8) ]

        self.children.RX = RX()
        self.children.TX = TX()

        self.children.RX.up()

        self._center_freq = GHz(135)
        self._offset_freq = MHz(10)
        self._udconv_div = 12
        
        self.children.LMX_Eravant = LMX2595Dev("Eravant", 2, 12, f_src=MHz(100), A=self.f_eravant, B=self.f_eravant/16, Apwr=3, Bpwr=0, Apd=False, Bpd=True)
        self.children.LMX_RX = LMX2595Dev("RX LO", 2, 13, f_src=MHz(100), A=self.f_UCSB, B=self.f_udconv, Apwr=0, Bpwr=32)
        self.children.LMX_TX = LMX2595Dev("TX LO", 2, 14, f_src=MHz(100), A=self.f_UCSB, B=self.f_udconv, Apwr=0, Bpwr=0)

        self.update_frequency_plan()

    def update_RX(self):
        self.children.LMX_RX.tune(self.f_UCSB, self.f_udconv)
        self.children.LMX_RX.program()        
        zcu111.children.rfdc.children.ADC[0].nco_freq = self.f_udconv

        # Why do I have to do this again?
        self.children.LMX_RX.Bpwr=24

    def print_frequency_plan(self):
        print(f"Frequency plan:")
        print(f" Eravant: f_LO: in: {self.f_eravant} out: {self.f_eravant*self.mult_eravant}")
        print(f" UCSB Freq: in: {self.f_UCSB} out: {self.f_UCSB*self.mult_UCSB}")
        print(f" RX VCO: {self.children.LMX_RX.config.VCO.f_out}")
        print(f" Converter freq: {self.f_udconv} NCO: {zcu111.children.rfdc.children.ADC[0].nco_freq}")
        
    @cmdproperty
    def f_center(self):
        return self._center_freq

    @f_center.setter
    def f_center(self, val):
        self._center_freq = val
        self.update_frequency_plan()
        
    @property
    def f_eravant(self):
        return round(((self.f_center + self.offset_freq) / self.mult_eravant), Hz(1))

    @property
    def f_UCSB(self):
        return round(self.f_center / self.mult_UCSB, Hz(1))

    @cmdproperty
    def udconv_div(self):
        return self._udconv_div

    @udconv_div.setter
    def udconv_div(self, s):
        assert s in [ 2, 3, 4, 6, 8, 12, 16, 24, 32 ]
        self._udconv_div = s
        self.update_frequency_plan()
        
    @property
    def f_udconv(self):
        return self.f_UCSB / self._udconv_div
    
    def update_eravant(self):
        self.children.LMX_Eravant.tune(self.f_eravant)
        
        self.children.LMX_Eravant.program()

    def update_TX(self):
        self.children.LMX_TX.program()
        
    def update_frequency_plan(self):
        self.update_eravant()
        self.update_RX()
        self.update_TX()
        self.print_frequency_plan()
        
    @command
    def load(self):
        p = os.path.dirname(os.path.abspath(__file__))
        
        os.system("fpgautil -b {p}/system.bin -m {p}/system.dtbo")

    @cmdproperty
    def offset_freq(self):
        return self._offset_freq

    @offset_freq.setter
    def offset_freq(self, v):
        self._offset_freq = v
        self.update_eravant()
    
class FW:
    path = os.path.dirname(os.path.abspath(__file__))

    binfile = f"{path}/system.bin"
    dtbofile = f"{path}/system.dtbo"
        
