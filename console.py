#!/usr/bin/env python3
from board_140GHz import PiRadio_140GHz_Bringup
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from pygments.lexer import RegexLexer
import pygments.token as pt
from functools import partial
from pathlib import Path

board = PiRadio_140GHz_Bringup()

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

        if self.last_token[0] == pt.Name:
            self.last_name = self.last_token[1]

    def NOTHING_BY_NAME(self):
        raise NothingByName(self.cur_obj, self.last_name, self.cur_token[1])
        
    def INCOMPLETE(self):
        cmpl = list(self.cur_obj.children) + list(self.cur_obj.verbs.keys())
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
            self.shift()

            if self.ntokens == 0:
                return
            
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

            args = verb.args
            nargs = len(args)

            argv = [  ]
        
            while nargs:
                nargs -= 1

            return partial(verb, *argv)
            
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
        ]
    }

    def pic_lex(self, s):
        t = self.get_tokens(s)

        return list(filter(lambda x: x[0] != pt.Text.Whitespace, t))
               
rlexer = PiCLexer()    
lexer = PygmentsLexer(PiCLexer)

class PiCCompleter(Completer):
    def get_completions(self, document, complete_event):
        p = PiCParser(board, list(rlexer.pic_lex(document.lines[0])))

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
    def validate(self, document):
        p = PiCParser(board, list(rlexer.pic_lex(document.text)))

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
        
while True:
    try:
        text = session.prompt(">",
                              completer=PiCCompleter(),
                              validator=PiCValidator(),
                              complete_while_typing=False,
                              lexer=lexer)
    except KeyboardInterrupt:
        continue
    except EOFError:
        break
    else:
        tokens = rlexer.pic_lex(text)
        p = PiCParser(board, tokens)
        try:
            cmd = p.parse()

            cmd()
        except Incomplete as e:
            print(f"Incomplete command {text} {e.c}")
            continue
        except BadSyntax:
            print("Syntax error")
            continue
        #except Exception as e:
        #    print(f"Command execution failure: {e}")
            
