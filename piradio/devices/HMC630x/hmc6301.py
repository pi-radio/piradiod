from piradio.command import command
from .hmc630x import HMC630x

class HMC6301(HMC630x):
    chip_addr=7

    def __init__(self, spi, csn):
        super().__init__(spi, csn)
        self._power = True


        self.bb_att1 = 0x3
        self.i_fine_att = 0
        self.q_fine_att = 0
        self.bb_att2 = 0x3
        
        # Enable external LO
        
        self.configure()

    @command
    def configure(self):
        if self._power:
            self.write_reg(0, 0)
            self.write_reg(1, 0x10 | (self.bb_att1 << 2))
        else:
            self.write_reg(0, 0xFF)
            self.write_reg(1, 0xF0 | (self.bb_att1 << 2))

        
        self.write_reg(2, (self.i_fine_att << 5) | (self.q_fine_att << 2) | self.bb_att2)
        # Can set high and low pass here
        self.write_reg(3, 0x03)
        self.write_reg(4, 0x9F)
        self.write_reg(5, 0x0F)
        self.write_reg(6, 0xBF)
        self.write_reg(7, 0x6D)
        self.write_reg(8, 0x80)
        self.write_reg(9, 0x40)
        self.write_reg(16, 0x36)
        self.write_reg(17, 0xBB)
        self.write_reg(18, 0x50)
        self.write_reg(19, 0x02)
        self.write_reg(20, 0x00)
        self.write_reg(21, 0x12)
        self.write_reg(22, 0x00)
        self.write_reg(23, 0x62)
        
    @command
    def powerdown(self):
        self._power = False
        self.configure()

    @command
    def powerup(self):
        self._power = True
        self.configure()
