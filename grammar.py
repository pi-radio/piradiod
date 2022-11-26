
grammar='''

statement: actor "." verb

verb: IDENTIFIER

actor: IDENTIFIER
     | actor "::" IDENTIFIER

IDENTIFIER: /[_A-Za-z][_A-Za-z0-9]*/

%import common.WS
'''
