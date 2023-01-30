#!/usr/bin/env python3
import re
import configparser

v = re.compile(r"R(?P<rno>[0-9]+)[\s]+0x(?P<val>[A-F0-9]+)")

config = configparser.ConfigParser()

config.read("LMX2595.ini")

bits = config['BITS']

fields = dict()
defaults = dict()

for i in range(101):
    s = f'{i:02d}'
    name = bits[f'NAME{s}'].lower().split('[')[0]
    
    defaults[name] = 0
    
regs = dict()
    
with open("HexRegisterValues.txt", "r") as hrv:
    for l in hrv:
        rno_s, rval_s = v.match(l).groups()

        rno = int(rno_s)
        rval = int(rval_s, 16) & 0xFFFF

        regs[rno] = rval

def bitfield(v, p, l):
    return ((v >> p) & ((1 << l) - 1))
        
for i in range(101):
    s = f'{i:02d}'
    name = re.split('[\[\:\]]', bits[f'NAME{s}'])
    reg = int(bits[f'REG{s}'][1:])
    pos = int(bits[f'POS{s}'])
    w = int(bits[f'LEN{s}'])

    fname = name[0].lower()

    #print(f"{fname} {name[1:]} {reg} {pos} {w} {defaults[fname]:x} {regs[reg]:04x}")
    
    if len(name) == 1:
        #print(name)
        defaults[fname] |= bitfield(regs[reg], pos, w)
    elif len(name) == 3:
        #print(name)
        assert(w == 1)
        defaults[fname] |= bitfield(regs[reg], pos, 1) << int(name[1])
    elif len(name) == 4:
        #print(f"{name[0]}[{name[1]}:{name[2]}] pos: {pos} w: {w}")
        assert(w == int(name[1]) - int(name[2]) + 1)
        defaults[fname] |= bitfield(regs[reg], pos, w) << int(name[2])        

    #print(f"now: {defaults[fname]:x}")


for k in sorted(defaults.keys()):
    v = defaults[k]
    print(f"{k}: 0x{v:x}")

