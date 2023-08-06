#!/usr/bin/env python3
import sys
import re
import configparser
import click
from pathlib import Path
from collections import defaultdict

bits_re = re.compile(r"(?P<field_name>[A-Za-z0-9_]+)\[(?P<start>[0-9]+)(:(?P<end>[0-9]+))?\]")

@click.command()
@click.argument('infile', type=click.Path(exists=True))
def parse_lmx_regs(infile):
    config = configparser.ConfigParser()

    config.read(infile)
    
    chip_id = Path(infile).name[3:7]
    classname = f"LMX{chip_id}Config"

    
    r = re.compile(r"(?P<entry_name>[A-Za-z]+)(?P<num>[0-9]+)(_[0-9]+)?")
    val_r = re.compile(r"(?P<entry_name>[A-Za-z]+)(?P<num>[0-9]+)")
    
    fields = dict()

    field_names = dict()

    rentry_map = dict()
    
    registers = dict()

    flexentry_map = dict()
    flexmap = dict()
    
    for k,v in config['REGISTERS'].items():
        if k == 'count' or k == 'description' or k == 'flexcount':
            continue

        try:
            m = r.match(k)

            entry = m.group('entry_name')
            num = int(m.group('num'))
        except:
            print(f"FAILURE: {k} {v}")
            continue

        if entry == 'name':
            n = int(v[1:])
            rentry_map[num] = n
            registers[n] = {}
            continue
        
        n = rentry_map[num]

        if entry == 'mask' or entry == 'value':
            registers[n][entry] = v
        elif entry == 'flexname':
            flexentry_map[num] = v
        elif entry == 'flexvalue':
            flexmap[flexentry_map[num]] = v
                
    for k,v in config['BITS'].items():
        if k == 'count' or k == 'description':
            continue
        
        try:
            m = r.match(k)

            entry = m.group('entry_name')
            num = int(m.group('num'))
        except:
            print(f"FAILURE: {k} {v}")
            continue
            
        if entry == 'name':
            field_names[num] = v
            fields[v] = { 'values': [] }
            continue

        field = field_names[num]
        
        if entry == 'val':
            fields[field]['values'].append(v)
            continue

        if entry == 'pos' or entry == 'len':
            v = int(v)
        
        fields[field][entry] = v

    reg_fields = defaultdict(list)

    reg_defaults = { int(k): int(v['value']) & 0xFFFF for k, v in registers.items() }

    for k,v in fields.items():
        rno = int(v['reg'][1:])
        reg_defaults[rno] &= ~(((1 << v['len']) - 1) << v['pos'])

    for k,v in fields.items():
        rno = int(v['reg'][1:])
        reg_fields[rno].append(k)

    full_fields = defaultdict(lambda: 0)
    
    for k, v in fields.items():
        m = bits_re.match(k)

        if m is not None:
            name = m.group('field_name')
        else:
            name = k

        full_fields[name] += v['len']
    
    def field_p(field_name):
        shift = 0
        length = 0
        
        if '[' in field_name:
            m = bits_re.match(field_name)
            field_name = m.group('field_name')
            if m.group('end') is None:
                shift = -int(m.group('start'))
            else:
                shift = -int(m.group('end'))
            length = -(int(m.group('start')) + shift)

        field = fields[field_name]
            
        shift += field['pos']
        length += field['len']

        sym = f"{field_name.lower()}"

        if shift == 0:
            return f"({sym} & 0x{((1 << (length + 1))-1):x})"        
        elif shift > 0:
            return f"(({sym} & 0x{((1 << (length + 1))-1):x}) << {shift})"
        else:
            return f"(({sym} >> {-shift}) & 0x{((1 << (length + 1))-1):x})"

    with open(f"include/piradio/lmx{chip_id}_config.hpp", "w") as f:
        f.write( "#pragma once\n")
        f.write( "\n")
        f.write( "#include <cstdint>\n")
        f.write( "#include <map>\n")
        f.write( "\n")
        f.write( "namespace piradio\n")
        f.write( "{\n")
        f.write(f"  class {classname}\n")
        f.write( "  {\n")
        for k, v in full_fields.items():
            if v >= 32:
                f.write( "    std::uint64_t ")
            elif v >= 16:
                f.write( "    std::uint32_t ")
            else:
                f.write( "    std::uint16_t ")
            f.write(f"{k.lower()};\n")

        f.write( "\n")

        f.write( "    void fill_regs(std::map<int, std::uint16_t> &map);\n")
        f.write( "    void read_regs(const std::map<int, std::uint16_t> &map);\n")
        f.write( "    void dump(void);\n")
        f.write( "  };\n")
        f.write( "};\n")
        
    def fill_r(field_name):
        return ""
        
    with open(f"src/lmx{chip_id}_config.cxx", "w") as f:
        f.write(f"#include <piradio/lmx{chip_id}_config.hpp>\n")
        f.write(f"#include <iostream>")
        f.write( "\n")
        f.write( "namespace piradio\n")
        f.write( "{\n")
        f.write(f"  void {classname}::fill_regs(std::map<int, uint16_t> &reg_vals)\n")
        f.write( "  {\n")
        for k, v in reg_fields.items():
            t = [ f"    reg_vals[{k}] = 0x{reg_defaults[k]:04x}" ]

            if len(v):
                t += [ field_p(field) for field in v ]
                
            f.write(" | ".join(t) + ";\n")
        f.write( "  }\n")

        f.write(f"  void {classname}::read_regs(const std::map<int, std::uint16_t> &reg_vals)\n")
        f.write( "  {\n")

        rnos = sorted(reg_defaults.keys())

        shift = 0
        length = 0
        
        for field_name, v in fields.items():
            shift = 0
            length = 0
            
            if '[' in field_name:
                print(field_name)
                m = bits_re.match(field_name)
                field_name = m.group('field_name').lower()
                start = int(m.group('start'))

                if m.group('end') is None:
                    end = start
                else:
                    end = int(m.group('end'))

                shift = end - v['pos']
                length = v['len']
                print(f"{start} {end} {length}")
                assert (start - end) + 1 == length
                mask = (1 << ((start - end) + 1)) - 1;

                typecast = ""
                if shift >= 16:
                    typecast = "(uint32_t)"
                if shift >= 32:
                    typecast = "(uint64_t)"
                f.write(f"    {field_name} = ({typecast}reg_vals.at({reg}) << {shift}) & 0x{mask:x};\n")
            else:                
                field_name = field_name.lower()

                reg = int(v['reg'][1:])
                shift += v['pos']
                length += v['len']

                mask = (1 << (length + 1)) - 1

                if shift == 0:
                    f.write(f"    {field_name} = reg_vals.at({reg}) & 0x{mask:x};\n")
                elif shift > 0:
                    f.write(f"    {field_name} = (reg_vals.at({reg}) >> {shift}) & 0x{mask:x};\n")
        f.write( "  }\n")

        f.write( "\n")
        f.write(f"  void {classname}::dump(void)\n")
        f.write( "  {\n")

        for k in full_fields:
            f.write(f'    std::cout << "{k.lower()}: " << {k.lower()} << std::endl;\n')
        f.write( "  }\n")
        f.write( "}\n")
        
if __name__ == '__main__':
    parse_lmx_regs()
