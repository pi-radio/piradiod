import time

from spidev import SPIDev

def set_bits(word, bits, start, l):
    word = (word & ~(((1 << l) - 1) << start))
    word |= (bits & ((1 << l) - 1)) << start
    return word

class MAX11300Port:    
    def __init__(self, device, i):
        self.device = device
        self.port_no = i
        
        self.config_r = self.device.read_reg(0x20+i) & 0xFFF
        
        print(f"Port {self.port_no} config: {self.config_r:3x}")
        
    def update_config(self):
        print(f"Updating port {self.port_no} config: {self.config_r:3x}")
        self.device.write_reg(0x20+self.port_no, self.config_r)
        return self.config_r
                
    @property
    def funcid(self):
        return (self.config_r >> 12) & 0xF

    @funcid.setter
    def funcid(self, v):
        print(self.config_r)
        print(v)
        self.config_r = set_bits(self.config_r, v, 12, 4)
        self.update_config()
        
    @property
    def inv(self):
        return (self.config_r >> 11) & 1

    @property
    def avr(self):
        return (self.config_r >> 11) & 1

    @property
    def range(self):
        return (self.config_r >> 8) & 0x7

    @range.setter
    def range(self, v):
        self.config_r = set_bits(self.config_r, v, 8, 3)
        self.update_config()
            
    @property
    def nsamples(self):
        return (self.config_r >> 5) & 0x7

    @property
    def assoc_port(self):
        return (self.config_r >> 0) & 0x1F

    @property
    def adc_value(self):
        return self.device.read_reg(0x40+self.port_no) & 0xFFF
            
    @property
    def dac_value(self):
        return self.device.read_reg(0x60+self.port_no) & 0xFFF

    @dac_value.setter
    def dac_value(self, v):
        print(f"Setting port {self.port_no} DAC value to {v}")
        self.device.write_reg(0x60+self.port_no, v & 0xFFF)
        return v

    @property
    def dac(self):
        if self.range == self.device.RANGE_DAC_0V_10V:
            return 10.0 * self.dac_value / 4096.0
        else:
            raise Exception("Unhandled range")

    @dac.setter
    def dac(self, v):
        if self.range == self.device.RANGE_DAC_0V_10V:
            assert(v >= 0 and v <= 10)
            self.dac_value = int(round(v * 4096.0 / 10.0))
        else:
            raise Exception("Unhandled range")
        
    
    def __str__(self):
        return f"<MAX11300 Port {self.port_no}>"

    
class MAX11300Dev(SPIDev):

    DEVCTL_ADCCTL_MASK = 3
    DEVCTL_ADCCTL_IDLE = 0
    DEVCTL_ADCCTL_SINGLESWEEP = 1
    DEVCTL_ADCCTL_SINGLECONVERSION = 2
    DEVCTL_ADCCTL_CONTINUOUS = 3

    DEVCTL_DACCTL_MASK = 3 << 2
    DEVCTL_DACCTL_SEQ = 0 << 2
    DEVCTL_DACCTL_IMM = 1 << 2
    DEVCTL_DACCTL_RSTDAT1 = 2 << 2
    DEVCTL_DACCTL_RSTDAT2 = 3 << 2

    DEVCTL_ADCRATE_MASK = 3 << 4
    DEVCTL_ADCRATE_200ksps = 0 << 4
    DEVCTL_ADCRATE_250ksps = 1 << 4
    DEVCTL_ADCRATE_333ksps = 2 << 4
    DEVCTL_ADCRATE_400ksps = 3 << 4

    DEVCTL_DACREF_MASK = 1 << 6
    DEVCTL_DACREF_EXT = 0 << 6
    DEVCTL_DACREF_INT = 1 << 6

    DEVCTL_THRSHDN_MASK = 1 << 7
    DEVCTL_THRSHDN_EN = 1 << 7

    DEVCTL_TMPCTL_MASK = 7 << 8
    DEVCTL_TMPCTL_MON_INT = 1 << 8
    DEVCTL_TMPCTL_MON_EXT1 = 1 << 9
    DEVCTL_TMPCTL_MON_EXT2 = 1 << 10

    DEVCTL_TMPPER_MASK = 1 << 11
    DEVCTL_TMPPER_ENABLE = 1 << 11

    DEVCTL_RSCANCEL_MASK = 1 << 12
    DEVCTL_RSCANCEL_ENABLE = 1 << 12

    DEVCTL_LPMODE_MASK = 1 << 13
    DEVCTL_LPMODE_ENABLE = 1 << 13
    
    DEVCTL_BURST_MASK = 1 << 14
    DEVCTL_BURST_ENABLE = 1 << 14

    DEVCTL_RESET_MASK = 1 << 15
    DEVCTL_RESET_ENABLE = 1 << 15

    RANGE_NONE = 0
    RANGE_DAC_0V_10V = 1
    RANGE_DAC_N5V_5V = 2
    RANGE_DAC_N10V_10V = 3
    RANGE_DAC_N5V_5V_2 = 4
    RANGE_DAC_0V_10V_2 = 6
    
    FUNCID_HIZ = 0
    FUNCID_GPI = 1
    FUNCID_BIDI = 2
    FUNCID_GPODAC = 3
    FUNCID_UPO = 4
    FUNCID_DAC = 5
    FUNCID_DAC_MONITOR = 6
    FUNCID_SEADC = 7
    FUNCID_DADCP = 8
    FUNCID_DADCN = 9
    FUNCID_DAC_DADCN = 10
    FUNCID_T2GPICAS = 11
    FUNCID_T2RCAS = 12
    
    def __init__(self, bus_no, dev_no, dac_ref=2.5):
        super().__init__(bus_no, dev_no)

        self.dac_ref = dac_ref

        if self.dev_id != 0b0000010000100100:
            raise Exception(f"Invalid dev id {self.dev_id}")

        self._ports = [ MAX11300Port(self, i) for i in range(20) ]       

        class PortList:
            device = self

            def __getitem__(self, i):
                return self.device._ports[i]

        self._port_list = PortList()

        print(f"dev_ctrl: {self.device_ctrl:04x}")
        
    def read_reg(self, reg_no):
        v = self.dev.transfer([ (reg_no << 1) | 0x1, 0x00, 0x00 ])

        return (v[1] << 8) | v[2]

    def write_reg(self, reg_no, v):
        r = self.dev.transfer([ reg_no << 1, (v >> 8) & 0xFF, v & 0xFF ])
        print(f"r: {r}")
        return v
    
    def read_20bit_reg(self, reg_no):
        v = self.dev.transfer([ reg_no | 0x1, 0x00, 0x00, 0x00, 0x00 ])

        return ((v[4] & 0xF) << 16) | (v[1] << 8) | v[2]
    
    @property
    def dev_id(self):
        return self.read_reg(0x00)
    
    @property
    def intr(self):
        return self.read_reg(0x01)

    @property
    def adc_status(self):
        return self.read_20bit_reg(0x02)
    
    @property
    def overcurrent(self):
        return self.read_20bit_reg(0x04)

    @property
    def gpi_status(self):
        return self.read_20bit_reg(0x06)

    @property
    def internal_temp_raw(self):
        return self.read_reg(0x08)

    @property
    def internal_temp(self):
        return self.internal_temp_raw * 0.125
    
    @property
    def external_temp0(self):
        return self.read_reg(0x09)

    @property
    def external_temp1(self):
        return self.read_reg(0x0A)

    @property
    def gpi_data(self):
        return self.read_20bit_reg(0x0B)

    @property
    def gpo_data(self):
        return self.read_20bit_reg(0x0D)

    @property
    def device_ctrl(self):
        return self.read_reg(0x10)

    @device_ctrl.setter
    def device_ctrl(self, v):
        self.write_reg(0x10, v)
        return v
    
    @property
    def intr_mask(self):
        return self.read_reg(0x11)

    @property
    def intr_mode0(self):
        return self.read_reg(0x12)
        
    @property
    def intr_mode1(self):
        return self.read_reg(0x13)
    
    @property
    def intr_mode2(self):
        return self.read_reg(0x14)

    @property
    def dac_preset0(self):
        return self.read_reg(0x16)

    @dac_preset0.setter
    def dac_preset0(self, v):
        self.write_reg(0x16, v & 0xFFF)
        return v
    
    @property
    def dac_preset1(self):
        return self.read_reg(0x17)

    @dac_preset1.setter
    def dac_preset1(self, v):
        self.write_reg(0x17, v & 0xFFF)
        return v

    
    @property
    def temp_mon(self):
        return self.read_reg(0x18)

    @property
    def temp_tresh_int_high(self):
        return self.read_reg(0x19)

    @property
    def temp_tresh_int_low(self):
        return self.read_reg(0x1A)

    @property
    def temp_tresh_ext0_high(self):
        return self.read_reg(0x1B)

    @property
    def temp_tresh_ext0_low(self):
        return self.read_reg(0x1C)

    @property
    def temp_tresh_ext1_high(self):
        return self.read_reg(0x1D)

    @property
    def temp_tresh_ext1_low(self):
        return self.read_reg(0x1E)

    @property
    def port(self):
        return self._port_list
            
    

    @property
    def adc(self):
        class ADCSet:
            device = self

            def __getitem__(self, i):
                assert(isinstance(i, int) and i >= 0 and i < 20)
                return self.device.read_reg(0x40+i) & 0xFFF;
            
        return ADCSet()

    @property
    def dac(self):
        class DACSet:
            device = self

            def __getitem__(self, i):
                assert(isinstance(i, int) and i >= 0 and i < 20)
                return self.device.read_reg(0x60+i) & 0xFFF;

            def __setitem__(self, i, v):
                assert(isinstance(i, int) and i >= 0 and i < 20)
                return self.device.write_reg(0x60+i, v) & 0xFFF;

        return DACSet()
