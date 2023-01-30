import os
import time

from piradio.command import CommandObject, command
from piradio.output import output
from piradio.devices import SPIDev
from piradio.devices import LTC5584Dev
from piradio.devices import LMX2595Dev
from piradio.devices import MAX11300Dev

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
    def __init__(self):
        print("Initializing 140GHz Bringup Board")

        self.children.LTC5584 = [ LTC5584Dev(2, i) for i in range(8) ]

        self.children.RX = RX()
        self.children.TX = TX()
        
        self.children.LMX_Eravant = LMX2595Dev(2, 12)
        self.children.LMX_RX = LMX2595Dev(2, 13)
        self.children.LMX_TX = LMX2595Dev(2, 14)

    @command
    def load(self):
        p = os.path.dirname(os.path.abspath(__file__))
        
        os.system("fpgautil -b {p}/system.bin -m {p}/system.dtbo")

class FW:
    path = os.path.dirname(os.path.abspath(__file__))

    binfile = f"{path}/system.bin"
    dtbofile = f"{path}/system.dtbo"
        
