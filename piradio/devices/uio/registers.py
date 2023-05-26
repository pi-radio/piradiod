class UIORegisterMetaclass(type):
    def __new__(cls, name, bases, dct):
        dct["__register__"] = True
        cls = super().__new__(cls, name, bases, dct)
        
        return cls
        
    def __getitem__(cls, n):
        return UIORegisterArray(cls, n)

class UIORegisterArray:
    def __init__(self, cls, n):
        self.cls = cls
        self.n = n

class UIOWindowInst:
    def __init__(self, obj, offset, size):
        print(f"Window inst {obj} {offset} {size}")
        self.obj = obj
        self.offset = offset
        self.size = size
        
    def __getitem__(self, a):
        return self.obj.csr[self.offset + a]
    
    def __setitem__(self, a, v):
        self.obj.csr[self.offset + a] = v


class UIOWindow:
    def __init__(self, offset, size, obj=None):
        print(f"UIO Window: {offset:x} {size:x} {obj}")
        self.offset = offset
        self.size = size
        self.obj = obj
        
    def __get__(self, obj, objtype):
        print(f"UIO Window __get__: {offset:x} {size:x} {obj}")
        return UIOWindowInst(obj, self.offset, self.size)

    @property
    def csr(self):
        print("Getting Window CSR")
        return UIOWindowInst(self.obj, self.offset, self.size)
    
class UIOWindowSet:
    def __init__(self, n, offset, size, stride, obj=None):
        print(f"UIO Window Set: {offset:x} {size:x} {stride:x} {obj}")
        self.n = n
        self.offset = offset
        self.size = size
        self.stride = stride
        self.obj = obj

    def __getitem__(self):
        pass
        
    def __get__(self, obj, objtype):
        return self.__class__(self.n, self.offset, self.size, self.stride, obj)
    
        print(f"UIO Window __get__: {offset:x} {size:x} {obj}")
        return UIOWindowInst(obj, self.offset, self.size)

    @property
    def csr(self):
        print("Getting Window CSR")
        return UIOWindowInst(self.obj, self.offset, self.size)
    
    
            
class UIORegister:
    def __init__(self, offset):
        self.offset = offset // 4

    def __get__(self, obj, objtype):
        print(f"UIO Reg: {self.offset}")
        return obj.csr[self.offset]

    def __set__(self, obj, v):
        obj.csr[self.offset] = v

