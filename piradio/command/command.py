import copy

cls_property = property().__class__

def command(f):
    f.args = f.__code__.co_varnames[:f.__code__.co_argcount][1:]
    f.picommand = True
    return f


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
            
            if isinstance(member, cls_property):
                retval.piproperties[mname] = member
                
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
    @property
    def name(self):
        return self.piname
    
    @property
    def children(self):
        if not hasattr(self, "_pichildren"):
            self._pichildren = CommandChildren()

        return self._pichildren

    @property
    def verbs(self):
        return self.picommands

    @property
    def properties(self):
        return self.piproperties

        
