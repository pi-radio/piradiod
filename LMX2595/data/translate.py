#!/usr/bin/env python3
import re
import configparser

v = re.compile(r"R(?P<rno>[0-9]+)[\s]+0x(?P<val>[A-F0-9]+)")

config = configparser.ConfigParser()

config.read("LMX2595.ini")

bits = config['BITS']

fields = dict()

for i in range(101):
    s = f'{i:02d}'
    name = bits[f'NAME{s}'].lower()

    reg = int(bits[f'REG{s}'][1:])
    pos = int(bits[f'POS{s}'])
    w = int(bits[f'LEN{s}'])
    
    if name[-1] == ']':
        t = re.split('[\[\:\]]', name)[:-1]
        if len(t) == 2:
            name = f"((self.LMX.{t[0]} >> {int(t[1])}) & 1)"
        elif len(t) == 3:
            name = f"bitfield(self.LMX.{t[0]}, {int(t[2])}, {int(t[1])-int(t[2])+1})"
        else:
            raise Exception("Unknown input")
    else:
        name = f"bitfield(self.LMX.{name}, 0, {w})"
        
    
    if reg not in fields:
        fields[reg] = list()

    fields[reg].append((name, pos, w))
    
with open("HexRegisterValues.txt", "r") as hrv:
    for l in hrv:
        rno_s, rval_s = v.match(l).groups()

        rno = int(rno_s)
        rval = int(rval_s, 16) & 0xFFFF

        print(f"        if rno == {rno}:")

        try:
            fl = fields[rno]
        except:
            print(f"            return 0x{rval:04x}")
            continue

        tail = ""
        
        for name, pos, w in fl:
            mask = (((1 << w) - 1) << pos)
            #print(f"{name} {pos} {w} {mask:04x} {rval:04x}")
            default = (rval & mask) >> pos
            rval &= ~mask
            #print(f"{rval:04x}")

        print(f"            return (0x{rval:04x}", end="")

        for name, pos, w in fl:
            print(f" | ({name} << {pos})", end="")

        print(f")")
            
