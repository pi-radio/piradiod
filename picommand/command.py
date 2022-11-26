
cls_property = property().__class__

def picommand(f):
    f.args = f.__code__.co_varnames[:f.__code__.co_argcount][1:]
    f.picommand = True
    return f


class PiCommandMetaclass(type):
    def __new__(cls, name, bases, dct):
        commands = {}
        properties = {}

        for mname, member in dct.items():
            try:
                if member.picommand == True:
                    commands[mname] = member
            except:
                pass
            
            if isinstance(member, cls_property):
                properties[mname] = member
                
        dct["__piname"] = name
        dct["__picommands"] = commands
        dct["verbs"] = property(lambda x: commands)
        dct["properties"] = property(lambda x: properties)
        
        return type.__new__(cls, name, bases, dct)


class PiCommandChildren:
    def __init__(self):
        self.__dict__["__children"] = dict()

    def __setattr__(self, n, v):
        assert isinstance(v, PiCommandObject) or isinstance(v, list)
        self.__dict__["__children"][n] = v

    def __getattr__(self, n):
        return self.__dict__["__children"][n]

    def __contains__(self, v):
        return v in self.__dict__["__children"]

    def __getitem__(self, n):
        return self.__dict__["__children"][n]

    def __iter__(self):
        return iter(self.__dict__["__children"])
    
class PiCommandObject(metaclass=PiCommandMetaclass):
    @property
    def name(self):
        return self.__piname
    
    @property
    def children(self):
        if not hasattr(self, "_pichildren"):
            self._pichildren = PiCommandChildren()

        return self._pichildren

    

        
