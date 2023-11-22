from functools import partialmethod
import inspect

from piradio.output import output

class TransitionDefinition:
    def __init__(self, from_state, to_state, f):
        self.from_state = from_state
        self.to_state = to_state
        self.f = f
        
class StateMachineMetaclass(type):
    def __new__(cls, name, bases, dct):
        if "states" not in dct:
            return super().__new__(cls, name, bases, dct)
        
        state_list  = dct["states"]
        state_names = [ s[0] for s in state_list ]


        def move_to_state(self, sname):
            self._change_state(sname)
        
        for s in state_names:                                
            dct[s] = partialmethod(move_to_state, s)

        dct["states"] = state_names
        
        assert dct["initial_state"] in state_names
            
        dct["initial"] = dct["initial_state"]
        dct["_fwd_transitions"] = { s[0]: dict() for s in state_list }
        dct["_rev_transitions"] = { s[0]: dict() for s in state_list }

        print(dct["_fwd_transitions"])
        print(dct["_rev_transitions"])
        
        for k, v in dct.items():
            if isinstance(v, TransitionDefinition):
                assert v.to_state not in dct["_fwd_transitions"][v.from_state]
                assert v.from_state not in dct["_rev_transitions"][v.from_state]
                
                dct["_fwd_transitions"][v.from_state][v.to_state] = v.f
                dct["_rev_transitions"][v.to_state][v.from_state] = v.f

        print(dct["_fwd_transitions"])
        print(dct["_rev_transitions"])

        retval = super().__new__(cls, name, bases, dct)

        return retval
    
class StateMachine(metaclass=StateMachineMetaclass):
    def __init__(self):
        self._state = self.initial
        
    @property
    def cur_state(self):
        return self._state

    def _change_state(self, ts):
        if self._state == ts:
            return
        
        p = self._find_state_path(ts)

        if p is None:
            raise RuntimeError(f"Unable to find state path from {self._state} to {ts}")

        assert p[0] == self._state
        
        for cs in p[1:]:
            print(f"Transition {self._state}->{cs}")
            self._fwd_transitions[self._state][cs](self)
            self._state = cs
            
    def _find_state_path(self, ts):
        paths = [ [ ts, ] ]
        visited = set([ts])
        
        while len(paths):
            p = paths[0]
            paths = paths[1:]
            
            for t in self._rev_transitions[p[-1]]:
                if t not in visited:
                    visited |= set([t])
                    if t == self._state:
                        return list(reversed(p + [ t ]))
                    paths.append(p + [ t ])

        return None

    
    def __getattr__(self, k):
        if k in self.states:
            return self.states[k]

        raise AttributeError(f"State machine doesn't have attribute {k}")
                
    
    def post_transition(self, start_state, end_state):
        pass

def register_states(cls):
    for state in cls.states:
        print(f"Adding state {state}")
        setattr(cls, state[0], export(property(lambda x: State(state[1], state[0] == cls.initial_state))))

    return cls


def transition(from_state, to_state):
    def make_transition(f):
        return TransitionDefinition(from_state, to_state, f)            

    return make_transition

def precondition(precond):
    def wrapper(f):
        def check_precond(obj):
            if not precond(obj):
                raise RuntimeError(f"Precondition not satisfied: {inspect.getsource(precond)}")
            return f(obj)

        return check_precond

    return wrapper

