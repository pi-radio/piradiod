from .register import Register
class bias:
    bias_ctrl = Register(name="bias_ctrl",addr=0x20,size=0x1,mask=0x7f,default=0x0)
    bias_vco_x3 = Register(name="bias_vco_x3",addr=0x21,size=0x1,mask=0x3,default=0x0)
    bias_pll = Register(name="bias_pll",addr=0x22,size=0x1,mask=0x37,default=0x0)
    bias_lo = Register(name="bias_lo",addr=0x23,size=0x1,mask=0x3f,default=0x0)
    bias_tx = Register(name="bias_tx",addr=0x24,size=0x2,mask=0xffff,default=0x0)
    bias_rx = Register(name="bias_rx",addr=0x26,size=0x2,mask=0xfff,default=0x0)

    bias_ctrl.doc = """LDO/Bias control
(1=enable)
Bits
0	BG1V1 for PLL current mirrot Enable
1	LDO VCO Enable
2	LDO for CP/PLL current mirror Enable
3	LDO CP Enable
4	LDO PLL current mirror Enable
5	Bias RF RX Enable
6	Bias RF TX Enable"""
    bias_vco_x3.doc = """Bias for VCO X3 out buffer
Bits
1:0	X3 out bias
X3 out bias
00	5.9 mA
01	7.2 mA
10	8.4 mA
11	9.7 mA"""
    bias_pll.doc = """Bias for PLL
Bits
2:0	Ibias ctrl
5:4	Ibias adjust
Ibias ctrl
000	Disable all
001	Enable Ref int
010	Enable Ref int, PFD
011	Enable Ref int, PFD, CHP
100	Enable Ref int, PFD, CHP, STM
101	Enable Ref int, PFD, CHP, STM, Div2
110	Enable Ref int, PFD, CHP, STM, Div2, DivN
111	Enable Ref int, PFD, CHP, STM, Div2, DivN, LD
Ibias adjust
00	80% of nominal bias
01	nominal bias
10	110% of nominal bias
11	136% of nominal bias"""
    bias_lo.doc = """Bias for LO X3
00	60% of nominal bias
01	80% of nominal bias
10	nominal bias
11	120% of nominal bias
Bits
1:0	LO X3 bias  21.2/2.2 mA (nom/off)
3:2	LO X3 TX buffer bias 10.6/1.1 mA (nom/off)
5:4	LO X3 RX buffer bias 10.6/1.1 mA (nom/off)"""
    bias_tx.doc = """Bias for TX-chain
00	60% of nominal bias
01	80% of nominal bias
10	nominal bias
11	120% of nominal bias
Bits
1:0	TX BB bias
3:2	TX VPA bias 16 x13.8/2.3 mA (nom/off)
5:4	TX VGA bias 16x21.7/0 mA (nom/off)
7:6	TX PA bias 16x28.4/4.5 mA (nom/off)
9:8	TX LO buffer mixer bias 30.3 mA (nom = bits 13:12)
11:10	TX IF buffer DC-level (nom = bits 13:12)
13:12	TX IF buffer bias ?10? mA (nom)
15:14	TX IF buffer bias fix"""
    bias_rx.doc = """Bias for RX-chain
00	60% of nominal bias
01	80% of nominal bias
10	nominal bias
11	120% of nominal bias
Bits
1:0	RX BB bias
3:2	RX VPA bias 16x11.6/2.26mA (nom/off)
5:4	RX VGA bias 16x19/0 mA (nom/off)
7:6	RX LNA bias 16x8.0/1.3 mA (nom/off)
9:8	RX mixer bias 10.7/4.1 mA (nom/off)
11:10	RX mixer LO bias 10.5/3 mA (nom/off)"""
    bias_ctrl.doc = """LDO/Bias control
(1=enable)
Bits
0	BG1V1 for PLL current mirrot Enable
1	LDO VCO Enable
2	LDO for CP/PLL current mirror Enable
3	LDO CP Enable
4	LDO PLL current mirror Enable
5	Bias RF RX Enable
6	Bias RF TX Enable"""
    bias_vco_x3.doc = """Bias for VCO X3 out buffer
Bits
1:0	X3 out bias
X3 out bias
00	5.9 mA
01	7.2 mA
10	8.4 mA
11	9.7 mA"""
    bias_pll.doc = """Bias for PLL
Bits
2:0	Ibias ctrl
5:4	Ibias adjust
Ibias ctrl
000	Disable all
001	Enable Ref int
010	Enable Ref int, PFD
011	Enable Ref int, PFD, CHP
100	Enable Ref int, PFD, CHP, STM
101	Enable Ref int, PFD, CHP, STM, Div2
110	Enable Ref int, PFD, CHP, STM, Div2, DivN
111	Enable Ref int, PFD, CHP, STM, Div2, DivN, LD
Ibias adjust
00	80% of nominal bias
01	nominal bias
10	110% of nominal bias
11	136% of nominal bias"""
    bias_lo.doc = """Bias for LO X3
00	60% of nominal bias
01	80% of nominal bias
10	nominal bias
11	120% of nominal bias
Bits
1:0	LO X3 bias  21.2/2.2 mA (nom/off)
3:2	LO X3 TX buffer bias 10.6/1.1 mA (nom/off)
5:4	LO X3 RX buffer bias 10.6/1.1 mA (nom/off)"""
    bias_tx.doc = """Bias for TX-chain
00	60% of nominal bias
01	80% of nominal bias
10	nominal bias
11	120% of nominal bias
Bits
1:0	TX BB bias
3:2	TX VPA bias 16 x13.8/2.3 mA (nom/off)
5:4	TX VGA bias 16x21.7/0 mA (nom/off)
7:6	TX PA bias 16x28.4/4.5 mA (nom/off)
9:8	TX LO buffer mixer bias 30.3 mA (nom = bits 13:12)
11:10	TX IF buffer DC-level (nom = bits 13:12)
13:12	TX IF buffer bias ?10? mA (nom)
15:14	TX IF buffer bias fix"""
    bias_rx.doc = """Bias for RX-chain
00	60% of nominal bias
01	80% of nominal bias
10	nominal bias
11	120% of nominal bias
Bits
1:0	RX BB bias
3:2	RX VPA bias 16x11.6/2.26mA (nom/off)
5:4	RX VGA bias 16x19/0 mA (nom/off)
7:6	RX LNA bias 16x8.0/1.3 mA (nom/off)
9:8	RX mixer bias 10.7/4.1 mA (nom/off)
11:10	RX mixer LO bias 10.5/3 mA (nom/off)"""
