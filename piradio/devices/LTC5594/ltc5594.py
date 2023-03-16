from piradio.devices.spidev import SPIDev
from piradio.output import output
from piradio.command import command, CommandObject

class LTC5594Dev(CommandObject):
    REG_LVCM_CF1 = 0x12
    REG_BAND = 0x13
    REG_CTRL = 0x16
    REG_CID = 0x17
    
    def __init__(self, spidev):
        self.spidev = spidev

        self.program()
        
        self.regs = [ self.read_reg(i) for i in range(0x18) ]

        print(self.regs)


    @command
    def program(self):
        lvcm = 0
        
        self.write_reg(self.REG_CTRL, 0xFC)
        self.write_reg(self.REG_CTRL, 0xF4)

        # Set Band, CF1, LF1, CF2
        # 1046-1242 = 1, 31, 3, 31
        band = 1
        lf1 = 3
        cf1 = 31
        cf2 = 31
        self.write_reg(self.REG_LVCM_CF1, (lvcm << 5) | cf1)
        self.write_reg(self.REG_BAND, (band << 7) | (lf1 << 5) | cf2)

        for i in range(16):
            self.write_reg(i, 0x80)
        
    @command
    def read_reg(self, reg_no : int):
        assert(reg_no < 0x18)
        r = self.spidev.xfer([ 0x80 | int(reg_no), 0 ])

        #output.print(f"LTC5594 Reg {reg_no:2x} {r[1]:2x}")
        
        return r[1]

    @command
    def write_reg(self, reg_no : int, v : int):
        assert(reg_no < 0x18)
        r = self.spidev.xfer([ int(reg_no), v ])

        return r[1]
