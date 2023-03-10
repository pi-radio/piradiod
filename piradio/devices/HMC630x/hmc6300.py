from .hmc630x import HMC630x

class HMC6300(HMC630x):
    chip_addr = 6

    def __init__(self, spi, csn):
        super().__init__(spi, csn)

        self.configure()

    def configure(self):
        self.write_reg(1, 0x4A)
        self.write_reg(2, 0xF2)
        self.write_reg(3, 0xF6)
        self.write_reg(4, 0x00)
        self.write_reg(5, 0xBF)
        self.write_reg(6, 0x6C)
        # Highest Gain
        self.write_reg(7, 0x0F)        

        # All presets
        self.write_reg(8, 0x8F)

        # Widest bandwidth (lowest Q)
        self.write_reg(9, 0xE0)

        # Digital IFVGA gain, power down temp sensor?
        self.write_reg(10, 0x51)

        # Highest RF gain
        self.write_reg(11, 0x03)

        # Turn off synthesizer
        self.write_reg(16, 0x00)
        self.write_reg(17, 0x00)
        self.write_reg(18, 0x50)
        self.write_reg(19, 0x02)
        self.write_reg(20, 0x00)
        self.write_reg(21, 0x12)
        self.write_reg(22, 0x00)
        self.write_reg(23, 0x62)
        
    def startup(self):
        #self.write_reg(2, 0)
        #self.write_reg(3, 3)
        #self.write_reg(4, 0x9F)
        #self.write_reg(5, 0x0F)
        #self.write_reg(6, 0xAF)
        #self.write_reg(7, 0x6C)
        #self.write_reg(8, 0x80)
        #self.write_reg(9, 0x0)
        #self.write_reg(18, 0x10)
        pass
        
