from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from pygments.lexer import RegexLexer
import pygments.token as pt
from functools import partial
from pathlib import Path
import inspect
import traceback
from .shutdown import shutdown

class PiCPException(Exception):
    pass

class NothingByName(PiCPException):
    def __init__(self, obj, parent, name):
        self.obj = obj
        self.parent = parent
        self.name = name
        
class NoVerb(PiCPException):
    def __init__(self, obj):
        self.obj = obj

class BadSyntax(PiCPException):
    def __init__(self, obj, tok):
        self.obj = obj
        self.tok = tok
        
class Incomplete(PiCPException):
    def __init__(self, obj, l, c):
        self.obj = obj
        self.l = l
        self.c = c

class PiCParser:
    def __init__(self, root_obj, tokens):
        self.cur_obj = root_obj
        self.tokens = tokens
        self.parse_result = None
        self.last_token = None
        self.last_name = "board"
        
    @property
    def cur_token(self):
        return self.tokens[0]

    @property
    def ntokens(self):
        return len(self.tokens)
    
    def shift(self):
        self.last_token = self.tokens[0]
        self.tokens = self.tokens[1:]

        if len(self.tokens) and self.tokens[0] == pt.Error:
            self.SYNTAX_ERROR()
        
        if self.last_token[0] == pt.Name:
            self.last_name = self.last_token[1]

    def need_shift(self):
        self.shift()

        if self.ntokens == 0:
            self.INCOMPLETE()

    def NOTHING_BY_NAME(self):
        raise NothingByName(self.cur_obj, self.last_name, self.cur_token[1])
        
    def INCOMPLETE(self):
        if isinstance(self.cur_obj, list):
            cmpl = list([ f"[{i}]" for i in range(len(self.cur_obj))])

            if self.last_token[0] == pt.Name:
                cmpl_len = 0
            elif self.last_token[1] == "[":
                cmpl_len = 1
            else:
                cmpl_len = len(self.last_token[1]) + 1
        else:
            cmpl = list(self.cur_obj.children) + list(self.cur_obj.verbs.keys()) + list(self.cur_obj.properties.keys())
            cmpl_len = 0

            if self.ntokens != 0 and self.cur_token[1] != ".":
                cmpl_len = len(self.cur_token[1])
                cmpl = list(filter(lambda x: x.startswith(self.cur_token[1]), cmpl))

                if len(cmpl) == 0:
                    self.NOTHING_BY_NAME()

        raise Incomplete(self.cur_obj, cmpl_len, cmpl)
            
    def SYNTAX_ERROR(self):
        raise BadSyntax(self.cur_obj, self.cur_token)
            
    def parse_scope(self):
        if self.ntokens == 0:
            self.INCOMPLETE()

        s = self.cur_token[1]
        
        if s in self.cur_obj.children:
            self.cur_obj = self.cur_obj.children[s]
            self.need_shift()
            
            if self.cur_token[1] == "[":
                if not isinstance(self.cur_obj, list):
                    self.SYNTAX_ERROR() # not really syntax, but too lazy to make new exception at the moment

                self.need_shift()

                if self.cur_token[0] != pt.Literal.Number:
                    self.SYNTAX_ERROR()
                
                try:
                    n = int(self.cur_token[1])
                    self.cur_obj = self.cur_obj[n]
                except ValueError:
                    self.SYNTAX_ERROR()

                self.need_shift()

                if self.cur_token[1] != "]":
                    self.SYNTAX_ERROR()

                self.need_shift()                
            
            if self.cur_token[1] == ".":
                self.shift()
                self.parse_scope()
    
    def parse(self):
        if self.ntokens == 0:
            self.INCOMPLETE()

        if self.cur_token[0] != pt.Name:
            self.SYNTAX_ERROR()

        self.parse_scope()

        if self.ntokens == 0:
            self.INCOMPLETE()

        if self.cur_token[1] in self.cur_obj.verbs:
            verb = getattr(self.cur_obj, self.cur_token[1])
            self.shift()
            
            sig = inspect.signature(verb)

            params = sig.parameters
            args = []

            for p in params.values():
                if self.ntokens == 0:
                    break

                if p.annotation:
                    args.append(p.annotation(self.cur_token[1]))
                else:
                    args.append(self.cur_token[1])

                self.shift()

            ba = sig.bind(*args)
            
            return partial(verb, *ba.args, **ba.kwargs)

        if self.cur_token[1] in self.cur_obj.properties:
            prop = self.cur_token[1]
            self.shift()

            if self.ntokens == 0:
                def show_property():
                    print(f"{getattr(self.cur_obj, prop)}")
                return show_property
            elif self.ntokens == 1:
                sig = inspect.signature(self.cur_obj.properties[prop].fset)

                i = iter(sig.parameters.values())
                next(i)

                val = next(i).annotation(self.cur_token[1])
                
                def set_property():
                    setattr(self.cur_obj, prop, val)

                return set_property
            else:
                self.SYNTAX_ERROR()  # Unexpected parameter
            
            
        elif self.cur_token[1] in self.cur_obj.properties:
            pass
        else:
            self.INCOMPLETE()


        

class PiCLexer(RegexLexer):
    name = "PiRadio"
    aliases = "pi-radio"
    filenames = "*.pic"

    tokens = {
        'root': [
            (r"[_A-Za-z][_A-Za-z0-9]*", pt.Name),
            (r"[ \n]+", pt.Whitespace),
            (r"\.", pt.Operator),
            (r"[+-]?[0-9]+(\\.[0-9]+)?(e[+-]?[0-9]+)?", pt.Literal.Number)
        ]
    }

    def pic_lex(self, s):
        t = self.get_tokens(s)

        return list(filter(lambda x: x[0] != pt.Text.Whitespace, t))
               
rlexer = PiCLexer()    
lexer = PygmentsLexer(PiCLexer)

class PiCCompleter(Completer):
    def __init__(self, root):
        self.root = root
        
    def get_completions(self, document, complete_event):
        p = PiCParser(self.root, list(rlexer.pic_lex(document.lines[0])))

        try:
            p.parse()
        except Incomplete as e:
            for c in e.c:
                yield Completion(c, start_position=-e.l)
        except NothingByName as e:
            pass
        except BadSyntax as e:
            pass

class PiCValidator(Validator):
    def __init__(self, root):
        self.root = root
        
    def validate(self, document):
        p = PiCParser(self.root, list(rlexer.pic_lex(document.text)))

        try:
            p.parse()
        except Incomplete as e:
            return
        except NothingByName as e:
            raise ValidationError(message=f"{e.parent} does not have a child or action {e.name}")
        except Exception as e:
            raise ValidationError(message=f"Unknown exception {e} in validation")


hist_dir = Path.home() / ".piradiod"

hist_dir.mkdir(parents=True, exist_ok=True)

session = PromptSession(history=FileHistory(hist_dir / "history"))


def command_loop(root):
    while True:
        try:
            text = session.prompt(">",
                                  completer=PiCCompleter(root),
                                  validator=PiCValidator(root),
                                  complete_while_typing=False,
                                  lexer=lexer)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            tokens = rlexer.pic_lex(text)
            p = PiCParser(root, tokens)
            try:
                cmd = p.parse()
                
                cmd()
            except Incomplete as e:
                print(f"Incomplete command {text} {e.c}")
                continue
            except BadSyntax:
                print("Syntax error")
                continue
            except Exception as e:
                print(''.join(traceback.format_exception(e)))
                break
            #except Exception as e:
            #    print(f"Command execution failure: {e}")
            
        
    shutdown.shutdown()
