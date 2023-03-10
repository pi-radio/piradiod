import time

class GPIOSPIController:
    def __init__(self, sck_gpio, mosi_gpio, miso_gpio):
        self.sck_gpio = sck_gpio
        self.mosi_gpio = mosi_gpio
        self.miso_gpio = miso_gpio

        sck_gpio.dir = "out"
        sck_gpio.val = 0
        mosi_gpio.dir = "out"
        sck_gpio.val = 0
        miso_gpio.dir = "in"

    def begin(self):
        self.bits_out = []
        self.bits_in = []
        
    def shift(self, bit_out):
        self.bits_out.append(bit_out)
        
        self.mosi_gpio.val = bit_out
        time.sleep(0.0001)
        self.sck_gpio.val = 1
        retval = self.miso_gpio.val
        time.sleep(0.0001)
        self.sck_gpio.val = 0
        time.sleep(0.0001)

        self.bits_in.append(retval)
        return retval

    def xfer_byte(self, v):
        retval = 0

        for i in range(8):
            retval = (retval << 1) | self.shift((v >> 7) & 0x1) 
            v <<= 1

        return retval
    
    def end(self):
        return (self.bits_out, self.bits_in)

    def get_device(self, cs_gpio):
        return GPIOSPIDevice(self, cs_gpio)
    
class GPIOSPIDevice:
    def __init__(self, controller, cs_gpio):
        self.controller = controller
        self.cs_gpio = cs_gpio

        
    def xfer(self, txn):
        self.controller.begin()
        
        self.cs_gpio.val = 0
        time.sleep(0.001)

        retval = [ self.controller.xfer_byte(byte) for byte in txn ]
                
        self.cs_gpio.val = 1

        bits_out, bits_in = self.controller.end()

        #print(f"Out: {bits_out} => In: {bits_in}")
        
        return retval
