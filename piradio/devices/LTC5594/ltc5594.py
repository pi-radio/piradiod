from piradio.devices.spidev import SPIDev
from piradio.output import output
from piradio.command import command, CommandObject

class LTC5594Dev(CommandObject):
    REG_LVCM_CF1 = 0x12
    REG_BAND = 0x13
    REG_CTRL = 0x16
    REG_CID = 0x17
    REG_AMP = 0x15
    
    def __init__(self, spidev):
        self.spidev = spidev


    @command
    def program(self):
        lvcm = 2

        self.write_reg(self.REG_CTRL, 0x0C, check=False)
        
        self.write_reg(self.REG_CTRL, 0xF0)

        #for i in range(16):
        #    self.write_reg(i, 0x80)

        # Set Band, CF1, LF1, CF2
        # 1046-1242 = 1, 31, 3, 31
        band = 1
        cf1 = 21
        lf1 = 3
        cf2 = 28
        self.write_reg(self.REG_LVCM_CF1, (lvcm << 5) | cf1)
        self.write_reg(self.REG_BAND, (band << 7) | (lf1 << 5) | cf2)

        pha = 0
        ampg = 0
        ampcc = 2
        ampic = 2

        self.write_reg(self.REG_AMP, ((pha & 1) << 7) | (ampg << 4) | (ampcc << 2) | ampic)
        
    @command
    def dump_regs(self):
        for i in range(0x18):
            v = self.read_reg(i)
            output.print(f"{i}: {v:02x}")
            
    @command
    def read_reg(self, reg_no : int):
        assert(reg_no < 0x18)
        r = self.spidev.xfer([ 0x80 | reg_no, 0 ])

        print(r)
        return r[1]

    @command
    def write_reg(self, reg_no : int, v : int, check=True):
        assert(reg_no < 0x18)
        r = self.spidev.xfer([ reg_no, v ])

        if check:
           vr = self.read_reg(reg_no)
           assert vr == v, f"Mismatch: {reg_no:x}: sent {v:x} got {vr:x}"
        
        return r[1]
