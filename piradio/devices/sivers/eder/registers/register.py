registers = dict()

def ffs(x):
    return (x&-x).bit_length()-1

class Register:
    def __init__(self, name, addr, size, default, mask=None):
        self.name = name
        self.addr = addr
        self.size = size
        self.default = default
        self.mask = mask

        if self.mask is not None:
            self.shift = ffs(mask)

        registers[name] = self

from math import ceil, log
### int -> list ###
def int2intlist(x, intmax=256, num_ints=0):
    """Convert x (integer) into list of integers.
       The size of each integer in the list can optionally be controlled
       by intmax so that the integer range is 0 to intmax-1 (default: 0-255).
       Number integers in the list can optionally be controlled by parameter num_ints,
       where num_ints=0 (default) means minimum number of integers required.
    """
    vals = []
    temp = x
    if (num_ints == 0):
        if (x != 0):
            num_ints=int(ceil(log(x,intmax)))
        else:
            num_ints = 1
    for i in range(num_ints-1,-1,-1):
        vals.append(int(temp//intmax**i))
        temp=temp%intmax**i
    return vals



### list -> int ###
def intlist2int(intlist, intmax=256):
    """Convert list of integers (range: 0 - intmax-1) to integer."""
    return reduce(lambda x, y: x * intmax + y, intlist)



### list -> list ###
def intlist2intlist(intlist,intmax_out,num_ints=0,intmax_in=256):
    return int2intlist(intlist2int(intlist,intmax_in),intmax_out,num_ints)

v = 0x0102030405060708090A
print(int2intlist(v))
print(list(v.to_bytes(10, 'big')))

def encode(v, n=2):
    return list(v.to_bytes(n, 'big'))

def decode(v, n=2):
    return int.from_bytes(bytearray(v), 'big')



        

class AttachedRegister:
    SPI_CMD_WRITE  = 0
    SPI_CMD_CLEAR  = 1
    SPI_CMD_SET    = 2
    SPI_CMD_TOGGLE = 3
    SPI_CMD_READ   = 4
    
    def __init__(self, spi, reg):
        self.spi = spi
        self.reg = reg

    def prefix(self, prefix):
        a = (self.reg.addr << 3) | prefix
        print(int2intlist(a,256, 2))
        print(encode(a))
        return encode(a)
    
    def __get__(self, obj, objtype=None):
        d = self.prefix(self.SPI_CMD_READ) + [ 0x00 ] * self.reg.size
        
        v = self.spi.xfer(d)

        # Convert v, maybe?
        v = decode(v[2:])

        if self.reg.mask is not None:
            v = (v & self.reg.mask) >> self.reg.shift

        return v
        
    def __set__(self, obj, x):
        cmd = self.SPI_CMD_WRITE
        if isinstance(x, bitop):
            cmd = x.cmd
            x = x.v

        d = self.prefix(cmd) + encode(x, self.reg.size)
            
        self.spi.xfer(d)
        
class bitop:
    def __init__(self, v):
        self.v = v

class toggle_bits(bitop):
    cmd = AttachedRegister.SPI_CMD_TOGGLE

class set_bits(bitop):
    cmd = AttachedRegister.SPI_CMD_SET

class clear_bits(bitop):
    cmd = AttachedRegister.SPI_CMD_CLEAR

def modify_bits(test, value):
    if test:
        return set_bits(value)
    else:
        return clear_bits(value)
        
        
def attach_registers(obj):
    class AttachedRegisters:
        def __init__(self, obj):
            obj.regs = self
        
    for k, v in registers.items():
        setattr(AttachedRegisters, k, AttachedRegister(obj.spi, v))

    AttachedRegisters(obj)

def generate_fake():
    l = [ 0 for i in range(1 << 13) ]

    for r in registers.values():
        l[r.addr:r.addr+r.size] = encode(r.default, r.size)

    return l
