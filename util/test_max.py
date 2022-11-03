#!/usr/bin/env python3
import time

from MAX11300 import MAX11300Dev

d = MAX11300Dev(2, 8)

print(f"{d.dev_id:b}")

print(f"Internal temp: {d.internal_temp}")


class HCVS:
    def __init__(self, MAX, base_port):
        self.base_port = base_port
        self.MAX = MAX

    def configure_ports(self):
        port = MAX.port[self.base_port]

        port.range = port.RANGE_DAC_0V_10V
#
# Left
#
#### InP Vbb Common
# Port 0 -- Opamp 0 DAC
# Port 1 -- Opamp 0 ADC High
# Port 2 -- Opamp 0 ADC low
# Port 3 -- Mixer VCM
#### Mix VLO Left
# Port 4 -- Opamp 1 DAC
# Port 5 -- Opamp 1 ADC High
# Port 6 -- Opamp 1 ADC low
#### x9 Vdd Left
# Port 7 -- Opamp 2 DAC
# Port 8 -- Opamp 2 ADC High
# Port 9 -- Opamp 2 ADC low
#### PA Vdd Left
# Port 10 -- Opamp 3 DAC
# Port 11 -- Opamp 3 ADC High
# Port 12 -- Opamp 3 ADC low
# Port 13 -- Bias VDD Left
# Port 14 -- x9 Vgs Left
# Port 15 -- PA Vgs Left
####### Right MAX
#### InP Vcc Common
# Port 0 -- Opamp 0 DAC
# Port 1 -- Opamp 0 ADC High
# Port 2 -- Opamp 0 ADC low
# Port 3 -- Mixer VCM Right
# Port 4 -- Opamp 1 DAC
# Port 5 -- Opamp 1 ADC High
# Port 6 -- Opamp 1 ADC low
# Port 7 -- Opamp 2 DAC
# Port 8 -- Opamp 2 ADC High
# Port 9 -- Opamp 2 ADC low
# Port 10 -- Opamp 3 DAC
# Port 11 -- Opamp 3 ADC High
# Port 12 -- Opamp 3 ADC low
# Port 13 -- Bias VDD Right
# Port 14 -- x9 Vgs Right
# Port 15 -- PA Vgs Right



#for i in range(20):
#    print(f"Port {i}: {d.port[i]}")

d.device_ctrl = (d.DEVCTL_ADCCTL_CONTINUOUS | d.DEVCTL_DACCTL_SEQ |
                 d.DEVCTL_ADCRATE_200ksps | d.DEVCTL_DACREF_INT |
                 d.DEVCTL_TMPCTL_MON_INT)

d.dac_preset0 = 256
d.dac_preset1 = 256

d.port[0].dac_value = 0

d.port[0].range = d.RANGE_DAC_0V_10V
d.port[0].funcid = d.FUNCID_DAC

time.sleep(1)

d.port[0].dac = 0.4

time.sleep(3)

print(f"DAC readback: {d.port[0].dac_value} {d.port[0].dac}")

print(f"{d.internal_temp}")

