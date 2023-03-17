import copy
import inspect

cls_property = property().__class__

cmdroot = None

def command(f):
    f.picommand = True
    return f

class cmdproperty:
    cmdproperty = True
    
    def __init__(self, 
                 fget=None, 
                 fset=None, 
                 fdel=None, 
                 doc=None):
        """Attributes of 'our_decorator'
        fget
            function to be used for getting 
            an attribute value
        fset
            function to be used for setting 
            an attribute value
        fdel
            function to be used for deleting 
            an attribute
        doc
            the docstring
        """
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)

class CommandMetaclass(type):
    def __new__(cls, name, bases, dct):
        retval = super().__new__(cls, name, bases, dct)

        retval.picommands = copy.copy(getattr(retval, "picommands", dict()))
        retval.piproperties = copy.copy(getattr(retval, "piproperties", dict()))
        
        for mname, member in dct.items():
            try:
                if member.picommand == True:
                    retval.picommands[mname] = member
            except:
                pass

            try:
                if member.cmdproperty == True:
                    retval.piproperties[mname] = member
            except:
                pass
            
        retval.piname = name

        return retval


class CommandChildren:
    def __init__(self):
        self.__dict__["__children"] = dict()

    def __setattr__(self, n, v):
        assert isinstance(v, CommandObject) or isinstance(v, list)
        self.__dict__["__children"][n] = v

    def __getattr__(self, n):
        return self.__dict__["__children"][n]

    def __contains__(self, v):
        return v in self.__dict__["__children"]

    def __getitem__(self, n):
        return self.__dict__["__children"][n]

    def __iter__(self):
        return iter(self.__dict__["__children"])
    
class CommandObject(metaclass=CommandMetaclass):
    def __getattr__(self, n):
        if n == "_pichildren":
            self._pichildren = CommandChildren()
            return self._pichildren
        
        if n in self._pichildren:
            return self._pichildren[n]

        try:
            return super().__getattr__(self, n)
        except AttributeError as e:
            raise AttributeError(f"{self.name} has no attribute or child {n}")
            
    @property
    def name(self):
        return self.piname
    
    @property
    def children(self):
        return self._pichildren

    @property
    def verbs(self):
        return self.picommands

    @property
    def properties(self):
        return self.piproperties

        
