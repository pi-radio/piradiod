from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.formatted_text import FormattedText

import pygments.token as pt
from functools import partial
from pathlib import Path
import logging
from lark import Lark, Transformer, logger
import lark
from lark.exceptions import *

import inspect
import traceback

from .shutdown import shutdown

from piradio.util import Freq
from piradio.output import output
from .command import CommandObject

#logger.setLevel(logging.DEBUG)

hist_dir = Path.home() / ".piradiod"

hist_dir.mkdir(parents=True, exist_ok=True)

session = PromptSession(history=FileHistory(hist_dir / "history"))


grammar = '''
start: call
     | open_scope -> incomplete_scope

call: call arg -> push_arg
    | scope -> start_call

scope: open_scope identifier -> child
     | scope "[" INT "]" -> array_entry
     | identifier -> scope_start

open_scope: scope "."

arg: SIGNED_NUMBER
   | ESCAPED_STRING
   | identifier
   | freq

freq: SIGNED_NUMBER freq_unit

freq_unit: GHZ
         | MHZ
         | KHZ
         | HZ
         | MILLIHZ
         | MICROHZ


identifier: CNAME

GHZ.10: "GHz"
MHZ.10: "MHz"
KHZ.10: "KHz"
HZ.10: "Hz"
MILLIHZ.10: "mHz"
MICROHZ.10: "uHz"


%import common.INT
%import common.NUMBER
%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%import common.CNAME
%import common.WS

%ignore WS



'''

class CommandError:
    def child(self, name):
        return self

    def push_arg(self, v):
        return self
    
class NothingByName(CommandError):
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name

    @property
    def message(self):
        return f"{self.name} is not a child of {self.obj}"
    
class Incomplete(CommandError):
    def __init__(self, obj, name, c):
        self.obj = obj
        self.name = name
        self.c = [ i for i in c if i.startswith(name) ]

    @property
    def l(self):
        return len(self.name)

    def open(self):
        return NothingByName(self.obj, self.name)

    def child(self, name):
        return self

    @property
    def message(self):
        return f"{self.name} is not a child of {self.obj}: possible completions: {self.c}"

    
class NotAnObject(CommandError):
    def __init__(self, obj):
        self.obj = obj

    @property
    def message(self):
        return f"{self.obj} is not a command object"

class NotPropOrMethod(CommandError):
    def __init__(self, obj):
        self.obj = obj

    @property
    def message(self):
        return f"{self.obj} is not a property or method"

class TooManyArguments(CommandError):
    def __init__(self, obj, n):
        self.obj = obj
        self.n = n

    @property
    def message(self):
        return f"{self.obj} expects at most {self.n} arguments"
    
class Property:
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name
        self.val = None
        
    def push_arg(self, v):
        if self.val is not None:
            return TooManyArguments(self.name, 1)

        self.val = v
        return self

    def __call__(self):
        if self.val is None:
            output.print(getattr(self.obj, self.name))
        else:
            setattr(self.obj, self.name, self.val)
        

class Command:
    def __init__(self, obj, name):
        self.obj = obj
        try:
            self.func = partial(getattr(obj, name))            
        except Exception as e:
            output.error(f"Failed to get partial: {obj} {name} {self.obj.picommands[name]}")
            raise e
            
    def push_arg(self, arg):
        try:
            sig = inspect.signature(self.func)
            _, param = next(iter(sig.parameters.items()))
            print(param)

            if param.annotation != inspect.Parameter.empty:
                arg = param.annotation(arg)
        
            self.func = partial(self.func, arg)
        
            return self
        except Exception as e:
            print(f"Error pusing arg: {arg} {sig}")
            traceback.print_exception(e)
            
    def __call__(self):
        self.func()
        
class OpenScope:
    def __init__(self, obj):
        self.obj = obj

    def child(self, name):
        if not isinstance(self.obj, CommandObject):
            return NotAnObject(self.obj)
                          
        if name in self.obj.children:
            return Scope(self.obj.children[name])

        if name in self.obj.picommands:
            return Command(self.obj, name)

        if name in self.obj.piproperties:
            return Property(self.obj, name)
    
        cmpl = [ s for s in self.all_completions ]

        if len(cmpl) == 0:
            return NothingByName(self.obj, name)

        return Incomplete(self.obj, name, cmpl)

    @property
    def all_completions(self):
        return (self.obj.children | self.obj.picommands.keys() | self.obj.piproperties.keys())

    def __call__(self):
        output.error(f"Incomplete scope: children {self.all_completions}")
    
class Scope:
    def __init__(self, obj):
        self.obj = obj

    def open(self):
        return OpenScope(self.obj)

    def push_arg(self, arg):
        return NotPropOrMethod(self.obj)
    
    def __getitem__(self, n):
        return Scope(self.obj[n])

class PCTransformer(Transformer):
    def __init__(self, root):
        self._root = OpenScope(root)

    def freq(self, tree):
        return Freq(tree[0], unit=tree[1])
        
    def freq_unit(self, tree):
        return tree[0]

    def arg(self, tree):
        return tree[0]
        
    def scope_start(self, tree):
        return self._root.child(tree[0])

    def open_scope(self, tree):
        return tree[0].open()

    def child(self, tree):
        return tree[0].child(tree[1])

    def identifier(self, tree):
        return tree[0]

    def incomplete_scope(self, tree):
        return tree[0]

    def start_call(self, tree):
        return tree[0]
    
    def push_arg(self, tree):
        return tree[0].push_arg(tree[1])
    
    def start(self, tree):
        return tree[0]

    def INT(self, tree):
        return int(tree[0])

    def ESCAPED_STRING(self, tree):
        return bytes(tree.value[1:-1], "utf-8").decode("unicode_escape")
    
    def SIGNED_NUMBER(self, tree):
        return float(tree)
    
    def array_entry(self, tree):
        return tree[0][tree[1]]

class PCCompleter(Completer):
    def __init__(self, parser):
        self.parser = parser
        
    def get_completions(self, document, complete_event):
        try:
            r = self.parser.parse(document.text)        

            if isinstance(r, OpenScope):
                for c in r.all_completions:
                    yield Completion(c, start_position=0)                
            if isinstance(r, Incomplete):
                for c in r.c:
                    yield Completion(c, start_position=-r.l)
        except Exception as e:
            output.error(f"Completer exception {e}")
                    
class PCValidator(Validator):
    def __init__(self, parser):
        self.parser = parser

    def validate(self, document):
        try:
            r = self.parser.parse(document.text)
        except UnexpectedToken:
            raise ValidationError(message=f"Unexpected token")
        except UnexpectedEOF:
            raise ValidationError(message=f"Unexpected end of line")
        except UnexpectedCharacters as e:
            raise ValidationError(message=f"Unexpected character '{e.char}' at column {e.column-1}")
        
        if isinstance(r, CommandError):
            raise ValidationError(message=r.message)
        
        if isinstance(r, Command):
            return

        if isinstance(r, Property):
            return

        raise ValidationError(message=f"Validation error: {r}")

            

        
class PCLexer(Lexer):
    def __init__(self, parser):
        self.parser = parser

    def lex_line(self, doc, lno):
        try:
            tl = self.parser.lex(doc.lines[lno])

            pos = 1

            retval = []
            
            for t in tl:
                if t.column != pos:
                    retval.append(('#ffffff', ' ' * (t.column - pos)))

                retval.append(('#ffffff', t))
                pos = t.end_column
                
            return retval        
        except UnexpectedCharacters as e:
            if e.token_history is not None:
                return [ ('#ffffff', t.value) for t in e.token_history ] + [('#ff0000', doc.lines[lno][e.column-1:])]
            return [ ('#ff0000', doc.lines[lno]) ]
        except Exception as e:
            return [ ('#ff0000', doc.lines[lno]) ]
        
    def lex_document(self, document):
        return partial(self.lex_line, document)


            
class PCParser:
    def __init__(self, root):
        self.parser = Lark(grammar, parser='lalr', propagate_positions=True)
        self.root = root

    def lex(self, s):
        return self.parser.lex(s)
        
    
    def parse(self, text):
        t = self.parser.parse(text)

        return PCTransformer(self.root).transform(t)

            
        
        
def command_loop(root):        
    parser = PCParser(root)
    
    while True:
        try:
            text = session.prompt(">",
                                  completer=PCCompleter(parser),
                                  validator=PCValidator(parser),
                                  complete_while_typing=False,
                                  validate_while_typing=False,
                                  lexer=PCLexer(parser))
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(''.join(traceback.format_exception(e)))
            break            
        else:
            try:
                cmd = parser.parse(text)

                cmd()
            except Exception as e:
                print(''.join(traceback.format_exception(e)))
        
    shutdown.shutdown()
