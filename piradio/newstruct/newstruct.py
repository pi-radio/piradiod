import sys
import inspect
import struct
from functools import partial

class NewStructMetaclass(type):
    def __new__(cls, name, bases, dct):
        if name == "Wrapper":
            name = bases[0].__name__
            
        cls = super().__new__(cls, name, bases, dct)
        
        return cls
        
    def __getitem__(cls, n):
        return NewStructArray(cls, n)

class NewStructArray(metaclass=NewStructMetaclass):
    __newstruct__ = True
    
    def __init__(self, cls, n):
        self._cls = cls
        self._n = n

    @property
    def name(self):
        return f"{self._cls.name}[{self._n}]"
    
    def get_val(self, buf):
        return [ self._cls.get_val(buf) for i in range(self._n) ]
        
#class NewStruct(metaclass=NewStructMetaclass):
#    pass
    
class AtomicType(metaclass=NewStructMetaclass):
    __newstruct__ = True
    
    def __init__(self, name, sf):
        self.name = name
        self.struct = struct.Struct(sf)
        
        
    def get_val(self, buf):
        return self.struct.unpack(buf.get_bytes(self.struct.size))[0]

    @property
    def aligned(self):
        return AlignedAtomic(self.struct.format)
        
class AlignedAtomic(AtomicType):
    def get_val(self, buf):
        sz = self.struct.size
        if buf._offset % sz != 0:
            print(f"!!!!!! Aligning {buf._offset} {sz}")
            buf.get_bytes(buf._offset % sz)
        return super().get_val(buf)
        
    
u32 = AtomicType('u32', 'I')
u64 = AtomicType('u64', 'Q')

addr = AtomicType('addr64', 'Q')

double =  AtomicType('double', 'd')


class StructBuf:
    def __init__(self, buf):
        self._buf = buf
        self._offset = 0

    def get_bytes(self, n):
        retval = self._buf[0:n]
        self._offset += n
        self._buf = self._buf[n:]
        return retval
        
    
def newstruct(cls):
    fields = dict()
    
    mro = inspect.getmro(cls)

    for c in mro[-1:0:-1]:
        if hasattr(c, "__newstruct__") and hasattr(c, "__wrapped__"):
            for k, v in inspect.get_annotations(c.__wrapped__).items():
                fields[k] = v

    for k, v in inspect.get_annotations(cls).items():
        fields[k] = v
        
    class Wrapper(cls, metaclass=NewStructMetaclass):
        __name__ = cls.__name__
        __wrapped__ = cls
        
        __newstruct__ = True

        __fields__ = fields

        name = cls.__name__
        
        def __init__(self, buf=None):
            if buf is None:
                return  # Empty struct
            
            self.unpack(StructBuf(buf))
            
        def unpack(self, buf):
            for k, v in self.__fields__.items():
                off = buf._offset
                if hasattr(v, "__newstruct__"):
                    cv = v.get_val(buf)
                    setattr(self, k, cv)
                    
        @classmethod
        def get_val(cls, buf):
            obj = cls()
            
            obj.unpack(buf)
            
            return obj

        def dump(self, indent=""):
            def iprint(s):
                print(f"{indent}{s}")
                
            for f, t in fields.items():
                v = getattr(self, f)
                
                if isinstance(t, AtomicType):
                    if isinstance(v, int):
                        iprint(f"{f}: 0x{v:x}")
                    else:
                        iprint(f"{f}: {v}")
                elif isinstance(v, list):
                    for i, elem in enumerate(v):
                        iprint(f"{f}[{i}]:")
                        elem.dump(indent=indent+" ")
                else:
                    v.dump(indent=indent+" ")
                        
                        
    return Wrapper
    
    


