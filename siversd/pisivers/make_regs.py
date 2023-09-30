from importlib.machinery import SourceFileLoader
from pathlib import Path
from collections import defaultdict
import sys
import re

mypath = Path(__file__).parent

p = Path(f"{Path(__file__).parent}/../../../../../PiSIVERS").absolute()

with open(p/"doc.py") as f:
    s = f.read()

class doc:
    exec(s)

with open(p/"register_table.py") as f:
    s = ""
    for l in f:
        if l.startswith("import"):
            continue
        s += l

class regs:
    exec(s)

for n in regs.regs:
    if n in regs.regs_mmf:
        if regs.regs[n] != regs.regs_mmf[n]:
            raise RuntimeError(f"Register {n} differs")
    else:
        print(f"{n} only in regs")
        print(f"{regs.regs[n]}")
        
for n in regs.regs_mmf:
    if n not in regs.regs:
        print(f"{n} only in regs_mmf")
        print(f"{regs.regs_mmf[n]}")

        
groupdefs = defaultdict(dict)

groupdoc = defaultdict(list)

def extract_regs(regs):
    for k, v in regs.items():
        group = v['group']

        if 'doc' in v:
            doc = v["doc"]
            groupdoc[group].append(f'    {k}.doc = """{doc}"""')

            del v['doc']

        def encval(v):
            try:
                return f"0x{int(v):x}"
            except:
                return f'"{v}"'

        del v['group']

        if 'value' in v:
            v['default'] = v['value']
            del v['value']
            
        s = f"{k} = Register("
        s += ",".join([ f'name="{k}"' ] + [f"{param}={encval(val)}" for param, val in v.items()])
        s += ")"
        
        if k in groupdefs[group]:
            assert groupdefs[group][k] == s
            
        groupdefs[group][k] = s

for k in dir(regs):
    if k[0] == "_":
        continue
    extract_regs(getattr(regs, k))
    

with open(mypath / "registers" / "__init__.py", "w") as f:
    print(f"from .register import attach_registers, generate_fake, toggle_bits, clear_bits, set_bits", file=f)
    for g in groupdefs:
        print(f"from .{g} import {g}", file=f)

for g, v in groupdefs.items():
    with open(mypath / "registers" / f"{g}.py", "w") as f:
        print(f"from .register import Register", file=f)
        print(f"class {g}:", file=f)
        for l in v.values():
            print(f"    {l}", file=f)

        print(file=f)
        for l in groupdoc[g]:
            print(l, file=f)

    
import registers

print(dir(registers))
