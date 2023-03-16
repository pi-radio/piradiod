from .hmc630x import HMC630x

class HMC6300(HMC630x):
    chip_addr = 6

    def __init__(self, spi, csn):
        super().__init__(spi, csn)

        self.configure()

    def configure(self):
        # binary 1100_1010 for normal operation
        self.write_reg(1, 0xCA)

        # 1111_1100 -- PA differential, TX PDET
        self.write_reg(2, 0xFC)

        # 1111_0110 -- High gain no temp
        self.write_reg(3, 0xF6)
        # POwer everything on here
        self.write_reg(4, 0x00)
        # 1111_1111 -- normal operation
        self.write_reg(5, 0xFF)
        # 1110_1100 -- normal operation
        self.write_reg(6, 0xEC)
        # Highest Gain
        self.write_reg(7, 0x0F)        

        # 1000_1111
        self.write_reg(8, 0x8F)

        # Widest bandwidth (lowest Q)
        # 1110_0000
        self.write_reg(9, 0xE0)

        # Digital IFVGA gain, power down temp sensor?
        # 0101_0001
        self.write_reg(10, 0x51)

        # Highest RF gain
        # 0000_0011
        self.write_reg(11, 0x03)

        # 0110_0100
        self.write_reg(12, 0x64)

        
        # Turn off synthesizer
        # 0000_0000
        self.write_reg(16, 0x00)

        # 0000_000 -- disabled synth
        self.write_reg(17, 0x00)

        # 0101_0000
        self.write_reg(18, 0x50)

        # 0000_0010
        self.write_reg(19, 0x02)

        # 0000_0000
        self.write_reg(20, 0x00)

        # 0001_0010
        self.write_reg(21, 0x12)

        # 0000_0000
        self.write_reg(22, 0x00)

        # 0110_0010
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
        
