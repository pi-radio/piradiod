from .register import Register
class pll:
    pll_en = Register(name="pll_en",addr=0x40,size=0x1,mask=0x7f,default=0x0)
    pll_divn = Register(name="pll_divn",addr=0x41,size=0x1,mask=0xff,default=0x0)
    pll_pfd = Register(name="pll_pfd",addr=0x42,size=0x1,mask=0x7,default=0x0)
    pll_chp = Register(name="pll_chp",addr=0x43,size=0x1,mask=0x73,default=0x0)
    pll_ld_mux_ctrl = Register(name="pll_ld_mux_ctrl",addr=0x44,size=0x1,mask=0xff,default=0x0)
    pll_test_mux_in = Register(name="pll_test_mux_in",addr=0x45,size=0x1,mask=0x3,default=0x0)
    pll_ref_in_lvds_en = Register(name="pll_ref_in_lvds_en",addr=0x46,size=0x1,mask=0x3,default=0x0)

    pll_en.doc = """PLL enable
Bits
0	DIVN enable
1	DIVBY2 Enable
2	Backlash (leak) Enable
3	LD enable
4	CHP Enable
5	PFD Enable
6	Low noise bias CHP Enable"""
    pll_divn.doc = """DIVN setting
Bits
2:0	S-count
7:3	P-count"""
    pll_pfd.doc = """PFD settings
Bits
0	PFD Test Enable
1	PFD Force up
2	PFD Force down"""
    pll_chp.doc = """CHP settings
Bits
1:0	CHP control
6:4	CHP leak
CHP control
00	CHP current 400 uA
01	CHP current 600 uA
10	CHP current 800 uA
11	CHP current 1 mA
CHP leak
000	Leak current 0 uA
001	Leak current 10 uA
010	Leak current 20 uA
011	Leak current 30 uA
100	Leak current 40 uA
101	Leak current 50 uA
110	Leak current 60 uA
111	Leak current 70 uA"""
    pll_ld_mux_ctrl.doc = """Lock detect control
Bits 2:0 value (Mux Control)
0	Filtered lock detect
1	XOR output
2	PLL reference (/2)
3	VCO divider (/2)
4	Unfiltered lock detect
5	PLL test mux bit 0
6	PLL test mux bit 1
7	Unused
Bits 5:4 value (Lock detect window)
0:	2 ns
1:	4 ns
2:	6 ns
3:	8 ns"""
    pll_test_mux_in.doc = """PLL test mux
Bits
0	Value for PLL test mux bit 0
1	Value for PLL test mux bit 1"""
    pll_ref_in_lvds_en.doc = """XO reference LVDS IO enable
Bits
0	1 = LVDS input, 0 = CMOS level input"""
    pll_en.doc = """PLL enable
Bits
0	DIVN enable
1	DIVBY2 Enable
2	Backlash (leak) Enable
3	LD enable
4	CHP Enable
5	PFD Enable
6	Low noise bias CHP Enable"""
    pll_divn.doc = """DIVN setting
Bits
2:0	S-count
7:3	P-count"""
    pll_pfd.doc = """PFD settings
Bits
0	PFD Test Enable
1	PFD Force up
2	PFD Force down"""
    pll_chp.doc = """CHP settings
Bits
1:0	CHP control
6:4	CHP leak
CHP control
00	CHP current 400 uA
01	CHP current 600 uA
10	CHP current 800 uA
11	CHP current 1 mA
CHP leak
000	Leak current 0 uA
001	Leak current 10 uA
010	Leak current 20 uA
011	Leak current 30 uA
100	Leak current 40 uA
101	Leak current 50 uA
110	Leak current 60 uA
111	Leak current 70 uA"""
    pll_ld_mux_ctrl.doc = """Lock detect control
Bits 2:0 value (Mux Control)
0	Filtered lock detect
1	XOR output
2	PLL reference (/2)
3	VCO divider (/2)
4	Unfiltered lock detect
5	PLL test mux bit 0
6	PLL test mux bit 1
7	Unused
Bits 5:4 value (Lock detect window)
0:	2 ns
1:	4 ns
2:	6 ns
3:	8 ns"""
    pll_test_mux_in.doc = """PLL test mux
Bits
0	Value for PLL test mux bit 0
1	Value for PLL test mux bit 1"""
    pll_ref_in_lvds_en.doc = """XO reference LVDS IO enable
Bits
0	1 = LVDS input, 0 = CMOS level input"""
