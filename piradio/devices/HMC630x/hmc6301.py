from piradio.command import command
from .hmc630x import HMC630x

class HMC6301(HMC630x):
    chip_addr=7

    def __init__(self, spi):
        super().__init__(spi)
        self._power = True


        self.bb_att1 = 0x0
        self.i_fine_att = 0
        self.q_fine_att = 0
        self.bb_att2 = 0x0
        self.bb_amp_hp = 0x00
        self.bb_amp_lp = 0x00
        
    @command
    def program(self):
        if self._power:
            self.write_reg(0, 0)
            self.write_reg(1, 0x00 | (self.bb_att1 << 2))
        else:
            self.write_reg(0, 0xFF)
            self.write_reg(1, 0xF0 | (self.bb_att1 << 2))

        
        self.write_reg(2, (self.i_fine_att << 5) | (self.q_fine_att << 2) | self.bb_att2)
        # Can set high and low pass here
        self.write_reg(3, (self.bb_amp_hp << 6) | (self.bb_amp_lp) << 4 | 0x3)
        self.write_reg(4, 0x9F)

        # HIghest IF gain
        self.write_reg(5, 0x0F)
        
        self.write_reg(6, 0xBF)
        self.write_reg(7, 0x6D)

        # Highest LNA gain
        self.write_reg(8, 0x87)
        
        self.write_reg(9, 0x40)

        self.write_reg(10, 0x00)
        self.write_reg(11, 0x00)
        self.write_reg(12, 0x00)
        self.write_reg(13, 0x00)
        self.write_reg(14, 0x00)


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
        self.write_reg(0, 0xFF)
        self._power = False

    @command
    def powerup(self):
        self.write_reg(0, 0x00)
        self._power = True

    @command
    def set_bw(self, lp : int, hp : int):
        self.bb_amp_hp = hp
        self.bb_amp_lp = lp
        self.write_reg(3, (self.bb_amp_hp << 6) | (self.bb_amp_lp) << 4 | 0x3)
        
