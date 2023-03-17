import time

class GPIOSPIController:
    def __init__(self, sck_gpio, mosi_gpio, miso_gpio):
        self.sck_gpio = sck_gpio
        self.mosi_gpio = mosi_gpio
        self.miso_gpio = miso_gpio

        sck_gpio.dir = "out"
        sck_gpio.val = 0

        mosi_gpio.dir = "out"
        mosi_gpio.val = 0
        
        miso_gpio.dir = "in"

    def shift(self, bit_out):
        self.mosi_gpio.val = bit_out
        self.delay()
        self.sck_gpio.val = 1
        retval = self.miso_gpio.val
        self.delay()
        self.sck_gpio.val = 0
        self.delay()

        return retval

    def xfer_byte(self, v):
        retval = 0

        for i in range(8):
            retval = (retval << 1) | self.shift((v >> 7) & 0x1) 
            v <<= 1

        return retval
    
    def get_device(self, cs_gpio):
        return GPIOSPIDevice(self, cs_gpio)

    def delay(self):
        time.sleep(0.0001)
    
class GPIOSPIDevice:
    def __init__(self, controller, cs_gpio):
        self.controller = controller
        self.cs_gpio = cs_gpio

        self.cs_gpio.dir = "out"
        self.cs_gpio.val = 1

    def delay(self):
        self.controller.delay()

    def long_delay(self):
        time.sleep(0.001)
        
    def begin(self):
        self.cs_gpio.val = 0
        self.long_delay()
                
    def end(self):
        self.cs_gpio.val = 1
        self.long_delay()
        
    def shift(self, bit_out):
        return self.controller.shift(bit_out)

    def dead_cycle(self):
        self.cs_gpio.val = 1
        self.long_delay()

        self.controller.shift(0)

        self.long_delay()
        self.cs_gpio.val = 0
        self.long_delay()
        
    def xfer(self, txn):        
        self.cs_gpio.val = 0
        self.long_delay()

        retval = [ self.controller.xfer_byte(byte) for byte in txn ]
                
        self.long_delay()
        self.cs_gpio.val = 1
        self.long_delay()
        
        return retval
