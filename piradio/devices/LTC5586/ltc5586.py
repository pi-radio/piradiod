from piradio.devices.spidev import SPIDev
from piradio.output import output
from piradio.command import command, CommandObject

class LTC5586Dev(CommandObject):
    def __init__(self, spidev):
        self.spidev = spidev
        self.regs = [ self.read_reg(i) for i in range(0x18) ]

    @command
    def read_reg(self, reg_no):
        reg_no = int(reg_no)
        assert(reg_no < 0x18)
        r = self.spidev.xfer([ 0x80 | int(reg_no), 0 ])

        #output.print(f"LTC5586 Reg {reg_no:2x} {r[1]:2x}")
        
        return r[1]
