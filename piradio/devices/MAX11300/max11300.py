import time

from piradio.devices.spidev import SPIDev
from piradio.output import output
from piradio.command import CommandObject, command

def set_bits(word, bits, start, l):
    word = (word & ~(((1 << l) - 1) << start))
    word |= (bits & ((1 << l) - 1)) << start
    return word

class MAX11300Port(CommandObject):    
    def __init__(self, device, i):
        self.device = device
        self.port_no = i
        self._batch = False
        self._config_dirty = False

        self.config_r = self.device.read_reg(0x20+i) & 0xFFF
        
        output.debug(f"Port {self.port_no} config: {self.config_r:3x}")

    def begin_config(self):
        self._batch = True

    def end_config(self):
        assert self._batch == True
        self._batch = False

        if self._config_dirty:
            self.update_config()
        
    def update_config(self):
        self._config_dirty = True

        if self._batch:
            return
        
        output.debug(f"Updating port {self.port_no} config: {self.config_r:3x}")
        self.device.write_reg(0x20+self.port_no, self.config_r)
        
        self._config_dirty = False
        return self.config_r
                
    @property
    def funcid(self):
        return (self.config_r >> 12) & 0xF

    @funcid.setter
    def funcid(self, v):
        self.config_r = set_bits(self.config_r, v, 12, 4)
        self.update_config()
        
    @property
    def inv(self):
        return (self.config_r >> 11) & 1

    @property
    def avr(self):
        return (self.config_r >> 11) & 1

    @avr.setter
    def avr(self, v):
        self.config_r &= ~((1 if v else 0) << 11)
        self.update_config()
    
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

    @assoc_port.setter
    def assoc_port(self, p):
        self.config_r = set_bits(self.config_r, p, 0, 5)
        self.update_config()
    
    @property
    def adc_value(self):
        return self.device.read_reg(0x40+self.port_no) & 0xFFF
            
    @property
    def dac_value(self):
        return self.device.read_reg(0x60+self.port_no) & 0xFFF

    @dac_value.setter
    def dac_value(self, v):
        self.device.write_reg(0x60+self.port_no, v & 0xFFF)
        return v

    @property
    def adc_range(self):
        return self.device.ranges[self.range][0]
    
    @property
    def dac_range(self):
        return self.device.ranges[self.range][1]
    
    @property
    def adc(self):
        while True:
            intr = self.device.intr
            status = self.device.adc_status

            if intr & 1:
                break
            
            time.sleep(0.010)
            
        r = self.adc_range
        v = self.adc_value
                
        if True:
            if v >= 2048:
                v = (v - 4096)/2048.0
            else:
                v = v / 2048.0
        else:
            v = v / 4096.0
            
        return (r[1]-r[0]) * v + r[0]

        
    @property
    def dac(self):
        r = self.dac_range

        return (r[1]-r[0]) * self.dac_value / 4096.0 + r[0]

    @dac.setter
    def dac(self, v):
        r = self.dac_range

        assert(v >= r[0] and v <= r[1])
        self.dac_value = int(round((v-r[0]) * 4096.0 / (r[1]-r[0])))
        

    @command
    def ramp_to(self, V, N=16, delay=0.01):
        assert(self.funcid == self.device.FUNCID_DAC or
               self.funcid == self.device.FUNCID_DAC_MONITOR)
        dV = (V - self.dac) / N

        for i in range(N - 1):
            self.dac += dV
            time.sleep(delay)
            
        self.dac = V
        
        
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

    DEVCTL_ADCRATE_200ksps = 0 
    DEVCTL_ADCRATE_250ksps = 1 
    DEVCTL_ADCRATE_333ksps = 2 
    DEVCTL_ADCRATE_400ksps = 3 

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

    ranges = [
        ((0,0),   (0,0)),
        ((0,10),  (0,10)),
        ((-5,5),  (-5,5)),
        ((-10,0), (-10,0)),
        ((0,2.5), (-5,5)),
        ((0,0),   (0,0)),
        ((0,2.5), (0,10))
    ]
    
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
        self._device_ctrl = None
        
        self.dac_ref = dac_ref

        if self.dev_id != 0b0000010000100100:
            raise Exception(f"Invalid dev id {self.dev_id}")

        self._ports = [ MAX11300Port(self, i) for i in range(20) ]       

        class PortList:
            device = self

            def __getitem__(self, i):
                return self.device._ports[i]

        self._port_list = PortList()

        output.debug(f"dev_ctrl: {self.device_ctrl:04x}")

        for p in self._ports:
            output.debug(f"Port {p}: {p.funcid}")
        
    def read_reg(self, reg_no):
        v = self.dev.transfer([ (reg_no << 1) | 0x1, 0x00, 0x00 ])

        return (v[1] << 8) | v[2]

    def write_reg(self, reg_no, v):
        r = self.dev.transfer([ reg_no << 1, (v >> 8) & 0xFF, v & 0xFF ])
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
        if self._device_ctrl is None:
            self._device_ctrl = self.read_reg(0x10)
            
        return self._device_ctrl

    @device_ctrl.setter
    def device_ctrl(self, v):
        self._device_ctrl = v
        self.write_reg(0x10, self._device_ctrl)
        return self._device_ctrl
    
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

    def setup(self, continuous=True, immediate=True, rate=400):
        c = self.DEVCTL_DACREF_INT

        if continuous:
            c |= 0x3

        if immediate:
            c = set_bits(c, 1, 2, 2)

        if rate == 400:
            c = set_bits(c, 3, 4, 2)

        self.device_ctrl = c
            
