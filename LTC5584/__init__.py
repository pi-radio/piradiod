from spidev import SPIDev

class LTC5584Dev(SPIDev):
    def __init__(self, bus_no, dev_no):
        super().__init__(bus_no, dev_no)

        self.regs = [ self.read_reg(i) for i in range(0x18) ]

    def read_reg(self, reg_no):
        assert(reg_no < 0x18)
        r = self.dev.transfer([ 0x80 | reg_no, 0 ])

        print(f"Reg {reg_no:2x} {r[1]:2x}")
        
        return r[1];
