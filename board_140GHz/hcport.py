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
            
        self.V = V

    def status(self, prefix=""):
        pioutput.print(f"{prefix}V: {1000.0*self.V:4.0f} mV Current: {1000.0*self.I:4.0f} mA")
        
