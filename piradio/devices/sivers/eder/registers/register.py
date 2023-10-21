from functools import reduce
from piradio.output import output

from contextlib import contextmanager

def ffs(x):
    return (x&-x).bit_length()-1

def encode(v, n=2):
    if isinstance(v, list):
        v = reduce(lambda x, y: x + y, [ i.to_bytes(n, 'big') for i in v ])
        
    if not isinstance(v, bytearray) and not isinstance(v, bytes):
        v = v.to_bytes(n, 'big')
    return list(v)

def decode(v, n=2):
    return int.from_bytes(bytearray(v), 'big')

class Registers:
    registers = dict()
    def __init__(self, obj, log_registers):
        self.spi = obj.spi
        self.log_registers = log_registers
        self.saved_registers = []

    def xfer(self, x):
        result = obj.spi.xfer(x)

        if self.log_registers:
            output.print("SPI: {x}=>{result}")

        return result

    @contextmanager
    def push_regs(self):
        self.saved_registers.append(dict())

        try:
            yield None
        finally:
            for k, v in self.saved_registers[-1].items():
                output.debug(f"Restoring registers: {k.name} 0x{v:x}")
                k.__set__(self, v)

            self.saved_registers.pop(-1)

    def forget(self, name):
        if self.registers[name] in self.saved_registers[-1]:
            del self.saved_registers[-1][self.registers[name]]

class AbstractRegister:
    SPI_CMD_WRITE  = 0
    SPI_CMD_CLEAR  = 1
    SPI_CMD_SET    = 2
    SPI_CMD_TOGGLE = 3
    SPI_CMD_READ   = 4

    def __init__(self, name, addr, size):
        self.name = name
        self.addr = addr
        self.size = size

    def prefix(self, prefix):
        return encode((self.addr << 3) | prefix)
    
    def __get__(self, obj, objtype=None):
        d = self.prefix(self.SPI_CMD_READ) + [ 0x00 ] * self.size
        
        v = obj.spi.xfer(d)

        # Convert v, maybe?
        v = decode(v[2:])

        if self.mask is not None:
            v = (v & self.mask) >> self.shift

        return v
            
    def __set__(self, obj, x):
        if obj.log_registers:
            output.print(f"Register Set {self.name} {x}")

        if (len(obj.saved_registers) and
            self not in obj.saved_registers[-1]):
            obj.saved_registers[-1][self] = self.__get__(obj)
            
        cmd = self.SPI_CMD_WRITE
        if isinstance(x, bitop):
            cmd = x.cmd
            x = x.v

        d = self.prefix(cmd) + encode(x, self.size) + [ 0x00 ]
            
        obj.spi.xfer(d)
        
class Register(AbstractRegister):
    def __init__(self, name, addr, size, default, mask=None):
        super().__init__(name, addr, size)
        self.name = name
        setattr(Registers, name, self)
        Registers.registers[name] = self
        self.default = default
        self.mask = mask

        if self.mask is not None:
            self.shift = ffs(mask)


class BFAzEntry:
    def __init__(self, spi, addr):
        self.spi = spi
        self.addr = addr
        self.log_registers = False
        self.saved_registers = []

    def set(self, v):
        assert len(v) == 32
        AbstractRegister("Az", self.addr, 32).__set__(self, v)
        
        
    def __getitem__(self, n):
        assert n < 16
        AbstractRegister("Az", self.addr + 2 * n, 2).__get__(self)
        
    def __setitem__(self, n, v):
        assert n < 16
        AbstractRegister("Az", self.addr + 2 * n, 2).__set__(self, v)

        
class BFRegisterInst:
    def __init__(self, spi, name, addr):
        self.spi = spi
        self.name = name
        self.addr = addr
        self.saved_registers = []

    def set(self, v):
        AbstractRegister("Bf", self.addr, 64 * 16 * 2).__set__(self, v)

    def __getitem__(self, n):
        assert n < 64
        return BFAzEntry(self.spi, self.addr + 32 * n)
        
    def __setitem__(self, n, v):
        assert n < 64
        AbstractRegister("Bf", self.addr + 32 * n, 32).__set__(self, v)
        
        
            
class BFRegister:
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        setattr(Registers, name, self)
        self.size = 64 * 16 * 2
        self.default = 0
        self.saved_registers = []

    def __get__(self, obj, objtype=None):
        return BFRegisterInst(obj.spi, self.name, self.addr)

    def __set__(self, obj, v):
        print(f"Setting {self.name} to {v}")
        BFRegisterInst(obj.spi, self.name, self.addr).set(v)
    
class bitop:
    def __init__(self, v):
        self.v = v

class toggle_bits(bitop):
    cmd = Register.SPI_CMD_TOGGLE

    def __repr__(self):
        return f"<toggle: {self.v:x}>"
    
class set_bits(bitop):
    cmd = Register.SPI_CMD_SET

    def __repr__(self):
        return f"<set: {self.v:x}>"
    
class clear_bits(bitop):
    cmd = Register.SPI_CMD_CLEAR

    def __repr__(self):
        return f"<clear: {self.v:x}>"
    
def modify_bits(test, value):
    if test:
        return set_bits(value)
    else:
        return clear_bits(value)
    
def attach_registers(obj, log_registers=False):
    obj.regs = Registers(obj, log_registers)
            
def generate_fake():
    l = [ 0 for i in range(1 << 13) ]

    for r in Registers.registers.values():
        l[r.addr:r.addr+r.size] = encode(r.default, r.size)

    return l
