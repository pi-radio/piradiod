import inspect

from piradio.output import output
from .command import CommandObject, CommandMetaclass

class TransInst:
    def __init__(self, trans, obj):
        self.trans = trans
        self.obj = obj

    def __call__(self):
        retval = self.trans.f(self.obj)
        self.obj._state = self.trans.end
        return retval
    
class Transition:
    def __init__(self, start, end, f):
        self.start = start
        self.end = end
        self.f = f

    def __get__(self, obj, objtype=None):
        return TransInst(self, obj)
        
    def invoke(self, obj):
        TransInst(self, obj)()

class StateInst:
    def __init__(self, state, obj):
        self.obj = obj
        self.state = state

    @property
    def in_trans(self):
        return self.state.in_trans
        
    @property
    def out_trans(self):
        return self.state.out_trans
        
    def __call__(self):
        p = self.state.find_path_from(self.obj.cur_state)

        for s in p[1:]:
            self.obj.cur_state.out_trans[s.name].invoke(self.obj)
                
    def __repr__(self):
        return f"<State {self.state.name}@{self.obj}>"

    def __eq__(self, other):
        if isinstance(other, State):
            return self.state == other
        if isinstance(other, StateInst):
            return self.state == other.state
        return False
    
class State:
    picommand = True
    def __init__(self, name, initial=False):        
        self.name = name
        self.initial=initial
        self.out_trans = dict()
        self.in_trans = dict()
        
    def _to_(self, other):
        def make_transition(f):
            t = Transition(self, other, f)

            assert other.name not in self.out_trans
            self.out_trans[other.name] = t

            assert self.name not in other.in_trans
            other.in_trans[self.name] = t
            
            return t

        return make_transition
        
    def __get__(self, obj, objtype=None):
        if obj == None:
            return self
        
        return StateInst(self, obj)
        
    def __repr__(self):
        return f"<State {self.name}>"

    def find_path_from(self, fs):
        paths = [ [ self, ] ]
        visited = set([self])
        
        while len(paths):
            p = paths[0]
            paths = paths[1:]
            
            for t in p[-1].in_trans.values():
                if t.start not in visited:
                    visited |= set([t.start])
                    if t.start == fs:
                        return list(reversed(p + [ t.start ]))
                    paths.append(p + [ t.start ])

        return None

class StateMachineMetaclass(CommandMetaclass):
    def __new__(cls, name, bases, dct):
        retval = super().__new__(cls, name, bases, dct)

        retval.states = dict()
        retval.initial = None
    
        for a, v in dct.items():
            if isinstance(v, State):
                if v.name in retval.states:
                    continue
                
                retval.states[v.name] = v
                if v.initial:
                    assert retval.initial is None, f"Initial state already defined: {retval.initial.name} {v.name}"                
                    retval.initial = v

        return retval
    
class StateMachine(CommandObject, metaclass=StateMachineMetaclass):
    def __init__(self):
        self._state = self.initial
        
    @property
    def cur_state(self):
        return self._state
        

def transition(from_state, to_state):
    def make_transition(f):
        t = Transition(from_state, to_state, f)

        assert to_state.name not in from_state.out_trans
        from_state.out_trans[to_state.name] = t

        assert from_state.name not in to_state.in_trans
        to_state.in_trans[from_state.name] = t
            
        return t

    return make_transition

def precondition(precond):
    def wrapper(f):
        def check_precond(obj):
            if not precond(obj):
                raise RuntimeError(f"Precondition not satisfied: {inspect.getsource(precond)}")
            return f(obj)

        return check_precond

    return wrapper

