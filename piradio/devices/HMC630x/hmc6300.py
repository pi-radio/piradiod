import time

from piradio.command import command

from .hmc630x import HMC630x

class HMC6300(HMC630x):
    chip_addr = 6

    def __init__(self, spi):
        super().__init__(spi)
       
    def program(self):
        self.write_reg(0, 0x00)
        self.write_reg(1, 0xCA)
        self.write_reg(2, 0xFD)
        self.write_reg(3, 0xF6)
        self.write_reg(4, 0x00)
        self.write_reg(5, 0xFF)
        self.write_reg(6, 0xEC)
        self.write_reg(7, 0x0F)        
        self.write_reg(8, 0x8F)
        self.write_reg(9, 0xE0)
        self.write_reg(10, 0x53)
        self.write_reg(11, 0x03)
        self.write_reg(12, 0x64)
        self.write_reg(13, 0x00)
        self.write_reg(14, 0x00)
        self.write_reg(15, 0x00)
        self.write_reg(16, 0x00)
        self.write_reg(17, 0xBB)
        self.write_reg(18, 0x00)
        self.write_reg(19, 0x02)
        self.write_reg(20, 0x00)
        self.write_reg(21, 0x12)
        self.write_reg(22, 0x00)
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
