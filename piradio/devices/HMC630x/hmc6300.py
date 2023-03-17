import time

from piradio.command import command

from .hmc630x import HMC630x

class HMC6300(HMC630x):
    chip_addr = 6

    def __init__(self, spi):
        super().__init__(spi)

    def program(self):
        self.write_reg(0, 0x00)
        # binary 1100_1010 (CAh) for normal operation
        self.write_reg(1, 0xCA)

        # 1111_1101 (FDh) -- PA differential, TX PDET
        # F3 in matlab, F1
        self.write_reg(2, 0xF1)

        # 1111_0110 (F6) -- High gain no temp
        # (Same as matlab)
        self.write_reg(3, 0xF6)

        
        # POwer everything on here
        self.write_reg(4, 0x00)
        
        # 1111_1111 (FF) -- normal operation
        # BF from Matlab
        self.write_reg(5, 0xBF)

        # 1110_1100 (EC) -- normal operation datasheet
        # 6c from Matlab
        self.write_reg(6, 0x6C)

        # Highest Gain (same as Matlab)        
        self.write_reg(7, 0x0F)        

        # 1000_1111 (same as Matlab)
        self.write_reg(8, 0x8F)

        # Widest bandwidth (lowest Q)
        # 1110_0000 (same as Matlab)
        self.write_reg(9, 0xE0)

        # Digital IFVGA gain, power down temp sensor?
        # 0101_0001 (same as Matlab)
        self.write_reg(10, 0x51)

        # Highest RF gain
        # 0000_0011 (same as Matlab)
        self.write_reg(11, 0x03)

        # 0110_0100 (64h)
        # 00h from Matlab
        #self.write_reg(12, 0x64)
        self.write_reg(12, 0)
        
        self.write_reg(13, 0)
        self.write_reg(14, 0)
        self.write_reg(15, 0)
                
        # Turn off synthesizer
        # 0000_0000
        # 36h in Matlab
        #self.write_reg(16, 0x00)
        self.write_reg(16, 0x36)

        # 0000_0000 -- disabled synth
        # BBh in Matlab
        self.write_reg(17, 0xBB)

        # 0101_0000 (50h) (Same as matlab)
        self.write_reg(18, 0x50)

        # 0000_0010 (02h) (Same as matlab)
        self.write_reg(19, 0x02)

        # 0000_0000 (00h) (Same as matlab)
        self.write_reg(20, 0x00)

        # 0001_0010 (12h) (Same as matlab)
        self.write_reg(21, 0x12)

        # 0000_0000 (00h) (Same as matlab)
        self.write_reg(22, 0x00)

        # 0110_0010 (62h) (Same as matlab)
        self.write_reg(23, 0x62)
        
    @command
    def powerdown(self):
        self.write_reg(4, 0xFF)

    @command
    def powerup(self):
        self.write_reg(4, 0x00)
        
    @command
    def dump_regs(self):
        for i in range(24):
            print(f"{i}: {self.read_reg(i):2x}")

    @command
    def regloop(self):
        while True:
            self.dump_regs()
            time.sleep(1)
