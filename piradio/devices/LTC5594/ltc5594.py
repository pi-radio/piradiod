from piradio.devices.spidev import SPIDev
from piradio.output import output
from piradio.command import command, CommandObject

def reg_property(n, start_bit=0, bit_len=8):
    mask = (1 << bit_len) - 1
    class reg_obj:
        def __get__(self, obj, objtype=None):
            return (obj.regs[n] >> start_bit) & mask

        def __set__(self, obj, value):
            obj.regs[n] = (obj.regs[n] &
                           ~(mask << start_bit) |
                           ((value & mask) << start_bit))
            obj.dirty[n] = True

    return reg_obj
                           
class LTC5594Dev(CommandObject):
    REG_LVCM_CF1 = 0x12
    REG_BAND = 0x13
    REG_CTRL = 0x16
    REG_CID = 0x17
    REG_AMP = 0x15
    
    def __init__(self, spidev):
        self.spidev = spidev

        self.regs = [ self.read_reg(i) for i in range(0x18) ]
        self.dirty = [ False ] * 0x18

        """
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
"""        

    im3qy = reg_property(0x00)
    im3qx = reg_property(0x01)
    im3iy = reg_property(0x02)
    im3ix = reg_property(0x03)
    im2qx = reg_property(0x04)
    im2ix = reg_property(0x05)
    hd3qy = reg_property(0x06)
    hd3qx = reg_property(0x07)
    hd3iy = reg_property(0x08)
    hd3ix = reg_property(0x09)
    hd2qy = reg_property(0x0A)
    hd2qx = reg_property(0x0B)
    hd2iy = reg_property(0x0C)
    hd2ix = reg_property(0x0D)
    dcoi = reg_property(0x0E)
    dcoq = reg_property(0x0F)

    ip3ic = reg_property(0x10, 0, 3)
    ip3cc = reg_property(0x11, 0, 2)

    gerr = reg_property(0x11, 2, 6)
    cf1 = reg_property(0x12, 0, 5)
    lvcm = reg_property(0x12, 5, 3)
    cf2 = reg_property(0x13, 0, 5)
    lf = reg_property(0x13, 5, 2)
    band = reg_property(0x13, 7, 1)
    
    ampic = reg_property(0x14, 0, 2)
    ampcc = reg_property(0x14, 2, 2)
    ampg = reg_property(0x14, 4, 3)

    edem = reg_property(0x16, 7, 1)
    edc = reg_property(0x16, 6, 1)
    eadj = reg_property(0x16, 5, 1)
    eamp = reg_property(0x16, 4, 1)

    sdo_mode = reg_property(0x16, 2, 1)
    
    @property
    def phase(self):
        return (self.regs(0x14) << 1) | (self.regs(0x15) >> 7)

    @phase.setter
    def phase(self, v):
        self.regs[0x14] = v >> 1
        self.regs[0x15] = (self.regs[0x15] & 0x7F) | ((v & 1) << 7)
    
    def _default_regs(self):
        # Boot-up defaults
        self._ampcc = 2
        self._ampic = 2
        self._ampg = 6
        self._band = 1
        self._cf1 = 8
        self._cf2 = 3
        self._dcoi = 0x80
        self._dcoq = 0x80
        self._eadj = 1
        self._eamp = 1
        self._edc = 1
        self._edem = 1
        self._gerr = 0x20
        self._hd2ix = 0x80
        self._hd2iy = 0x80
        self._hd2qx = 0x80
        self._hd2qy = 0x80
        self._hd3ix = 0x80
        self._hd3iy = 0x80
        self._hd3qx = 0x80
        self._hd3qy = 0x80
        self._im2ix = 0x80
        self._im2qx = 0x80
        self._im3ix = 0x80
        self._im3qx = 0x80
        self._im3iy = 0x80
        self._im3qy = 0x80

        self._ip3cc = 0x02
        self._ip3ic = 0x04

        self._lf1 = 0x03
        self._lvcm = 0x02
        self._pha = 0x100
        self._sdo_mode = 0

    @command
    def program(self):
        for i, d in enumerate(self.dirty):
            if not d:
                continue

            self.write_reg(i)
            self.dirty[i] = False
                                   
    @command
    def dump_regs(self):
        for i in range(0x18):
            v = self.read_reg(i)
            output.print(f"{i}: {v:02x}")
            
    @command
    def read_reg(self, reg_no : int):
        assert(reg_no < 0x18)
        r = self.spidev.xfer([ 0x80 | reg_no, 0 ])

        return r[1]

    @command
    def write_reg(self, reg_no : int, check=True):
        assert(reg_no < 0x18)
        r = self.spidev.xfer([ reg_no, self.regs[reg_no] ])
        self.dirty[reg_no] = False

        if check and reg_no != 0x16:
           vr = self.read_reg(reg_no)
           assert vr == v, f"Mismatch: {reg_no:x}: sent {v:x} got {vr:x}"
        
        return r[1]
