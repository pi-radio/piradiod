from .register import Register
class trx:
    trx_ctrl = Register(name="trx_ctrl",addr=0x1c0,size=0x1,mask=0x3b,default=0x0)
    trx_soft_ctrl = Register(name="trx_soft_ctrl",addr=0x1c1,size=0x1,mask=0x3,default=0x0)
    trx_soft_delay = Register(name="trx_soft_delay",addr=0x1c2,size=0x1,mask=0x7,default=0x0)
    trx_soft_max_state = Register(name="trx_soft_max_state",addr=0x1c3,size=0x1,mask=0x7,default=0x0)
    trx_tx_on = Register(name="trx_tx_on",addr=0x1c4,size=0x3,mask=0x1fffff,default=0x1fffff)
    trx_tx_off = Register(name="trx_tx_off",addr=0x1c7,size=0x3,mask=0x1fffff,default=0x0)
    trx_rx_on = Register(name="trx_rx_on",addr=0x1ca,size=0x3,mask=0x1fffff,default=0x1fffff)
    trx_rx_off = Register(name="trx_rx_off",addr=0x1cd,size=0x3,mask=0x1fffff,default=0x0)
    trx_soft_tx_on_enables = Register(name="trx_soft_tx_on_enables",addr=0x1e0,size=0x8,mask=0x1f1f1f1f1f1f1f1f,default=0x0)
    trx_soft_rx_on_enables = Register(name="trx_soft_rx_on_enables",addr=0x1e8,size=0x8,mask=0x1f1f1f1f1f1f1f1f,default=0x0)
    trx_soft_bf_on_grp_sel = Register(name="trx_soft_bf_on_grp_sel",addr=0x1f0,size=0x4,mask=0xffffffff,default=0x0)

    trx_ctrl.doc = """TX/RX enable control (1=enable)
TX/RX-switching together with TX ALC and/or TX/RX Soft switch functions should only
be performed when GPIO Control is enabled, or else proper functionality of TX ALC and/or
TX/RX Soft switch cannot be guaranted.

Bits 3:0
0	RX Enable
1	TX Enable
3	GPIO Control Enable
4	RX Soft switch enable
5	TX Soft switch enable"""
    trx_soft_ctrl.doc = """TX/RX Soft switch enable control
Bits 5:4 in register trx_ctrl are the same as bits 1:0 in this register.
Bits
0	RX Soft switch enable
1	TX Soft switch enable"""
    trx_soft_delay.doc = """TX/RX Soft switch delay
Bits
2:0	Delay for each enable/disable state"""
    trx_soft_max_state.doc = """TX/RX Soft switch maximum/last state
Bits
2:0	Maximum/Last state for soft switch"""
    trx_tx_on.doc = """TX bias on control when TX mode is active

Bits
20	Enable TX PA bias loop
19	Enable TX BF VGAs
18	Enable TX Q Baseband
17	Enable TX I Baseband
16	Enable TX mixer- and LO-buffer, RF VGA and common PA
15:0	Enable TX BF ports 15-0"""
    trx_tx_off.doc = """TX bias on control when TX mode is inactive

Bits
20	Enable TX PA bias loop
19	Enable TX BF VGAs
18	Enable TX Q Baseband
17	Enable TX I Baseband
16	Enable TX mixer- and LO-buffer, RF VGA and common PA
15:0	Enable TX BF ports 15-0"""
    trx_rx_on.doc = """RX bias on control when RX mode is active

Bits
20	Enable RX Q Baseband Output buffer
19	Enable RX Q Baseband Input Buffer, VGA1-3
18	Enable RX I Baseband Output buffer
17	Enable RX I Baseband Input Buffer, VGA1-3
16	Enable RX mixer- and LO-buffer, RF VGA
15:0	Enable RX BF ports 15-0"""
    trx_rx_off.doc = """RX bias on control when RX mode is inactive

Bits
20	Enable RX Q Baseband Output buffer
19	Enable RX Q Baseband Input Buffer, VGA1-3
18	Enable RX I Baseband Output buffer
17	Enable RX I Baseband Input Buffer, VGA1-3
16	Enable RX mixer- and LO-buffer, RF VGA
15:0	Enable RX BF ports 15-0"""
    trx_soft_tx_on_enables.doc = """TX/RX Soft switch TX mode transition enables

TX Enables (bits 19:16 in register trx_tx_on)
4	Enable TX PA bias loop
3	Enable TX BF VGAs
2	Enable TX Q Baseband
1	Enable TX I Baseband
0	Enable TX mixer- and LO-buffer, RF VGA and common PA

Bits
60:56	TX enables for state 0
52:48	TX enables for state 1
44:40	TX enables for state 2
36:32	TX enables for state 3
28:24	TX enables for state 4
20:16	TX enables for state 5
12:8	TX enables for state 6
4:0	TX enables for state 7"""
    trx_soft_rx_on_enables.doc = """TX/RX Soft switch RX mode transition enables

RX Enables (bits 17:16 in register trx_rx_on)
4	Enable RX Q Baseband Output buffer
3	Enable RX Q Baseband Input Buffer, VGA1-3
2	Enable RX I Baseband Output buffer
1	Enable RX I Baseband Input Buffer, VGA1-3
0	Enable RX mixer- and LO-buffer, RF VGA

Bits
60:56	RX enables for state 0
52:48	RX enables for state 1
44:40	RX enables for state 2
36:32	RX enables for state 3
28:24	RX enables for state 4
20:16	RX enables for state 5
12:8	RX enables for state 6
4:0	RX enables for state 7"""
    trx_soft_bf_on_grp_sel.doc = """TX/RX Soft switch BF element enable group select

Group select	BF element enables
0000		0x0000
0001		0x0180
0010		0x03C0
0011		0x07E0
0100		0x0FF0
0101		0x1FF8
0110		0x3FFC
0111		0x7FFE
1000		0xFFFF
1001		0x8001
1010		0xC003
1011		0xE007
1100		0xF00F
1101		0xF81F
1110		0xFC3F
1111		0xFE7F

Bits
31:28	Group select for state 0
27:24	Group select for state 1
23:20	Group select for state 2
19:16	Group select for state 3
15:12	Group select for state 4
11:8	Group select for state 5
7:4	Group select for state 6
3:0	Group select for state 7"""
    trx_ctrl.doc = """TX/RX enable control (1=enable)
TX/RX-switching together with TX ALC and/or TX/RX Soft switch functions should only
be performed when GPIO Control is enabled, or else proper functionality of TX ALC and/or
TX/RX Soft switch cannot be guaranted.

Bits 3:0
0	RX Enable
1	TX Enable
3	GPIO Control Enable
4	RX Soft switch enable
5	TX Soft switch enable"""
    trx_soft_ctrl.doc = """TX/RX Soft switch enable control
Bits 5:4 in register trx_ctrl are the same as bits 1:0 in this register.
Bits
0	RX Soft switch enable
1	TX Soft switch enable"""
    trx_soft_delay.doc = """TX/RX Soft switch delay
Bits
2:0	Delay for each enable/disable state"""
    trx_soft_max_state.doc = """TX/RX Soft switch maximum/last state
Bits
2:0	Maximum/Last state for soft switch"""
    trx_tx_on.doc = """TX bias on control when TX mode is active

Bits
20	Enable TX PA bias loop
19	Enable TX BF VGAs
18	Enable TX Q Baseband
17	Enable TX I Baseband
16	Enable TX mixer- and LO-buffer, RF VGA and common PA
15:0	Enable TX BF ports 15-0"""
    trx_tx_off.doc = """TX bias on control when TX mode is inactive

Bits
20	Enable TX PA bias loop
19	Enable TX BF VGAs
18	Enable TX Q Baseband
17	Enable TX I Baseband
16	Enable TX mixer- and LO-buffer, RF VGA and common PA
15:0	Enable TX BF ports 15-0"""
    trx_rx_on.doc = """RX bias on control when RX mode is active

Bits
20	Enable RX Q Baseband Output buffer
19	Enable RX Q Baseband Input Buffer, VGA1-3
18	Enable RX I Baseband Output buffer
17	Enable RX I Baseband Input Buffer, VGA1-3
16	Enable RX mixer- and LO-buffer, RF VGA
15:0	Enable RX BF ports 15-0"""
    trx_rx_off.doc = """RX bias on control when RX mode is inactive

Bits
20	Enable RX Q Baseband Output buffer
19	Enable RX Q Baseband Input Buffer, VGA1-3
18	Enable RX I Baseband Output buffer
17	Enable RX I Baseband Input Buffer, VGA1-3
16	Enable RX mixer- and LO-buffer, RF VGA
15:0	Enable RX BF ports 15-0"""
    trx_soft_tx_on_enables.doc = """TX/RX Soft switch TX mode transition enables

TX Enables (bits 19:16 in register trx_tx_on)
4	Enable TX PA bias loop
3	Enable TX BF VGAs
2	Enable TX Q Baseband
1	Enable TX I Baseband
0	Enable TX mixer- and LO-buffer, RF VGA and common PA

Bits
60:56	TX enables for state 0
52:48	TX enables for state 1
44:40	TX enables for state 2
36:32	TX enables for state 3
28:24	TX enables for state 4
20:16	TX enables for state 5
12:8	TX enables for state 6
4:0	TX enables for state 7"""
    trx_soft_rx_on_enables.doc = """TX/RX Soft switch RX mode transition enables

RX Enables (bits 17:16 in register trx_rx_on)
4	Enable RX Q Baseband Output buffer
3	Enable RX Q Baseband Input Buffer, VGA1-3
2	Enable RX I Baseband Output buffer
1	Enable RX I Baseband Input Buffer, VGA1-3
0	Enable RX mixer- and LO-buffer, RF VGA

Bits
60:56	RX enables for state 0
52:48	RX enables for state 1
44:40	RX enables for state 2
36:32	RX enables for state 3
28:24	RX enables for state 4
20:16	RX enables for state 5
12:8	RX enables for state 6
4:0	RX enables for state 7"""
    trx_soft_bf_on_grp_sel.doc = """TX/RX Soft switch BF element enable group select

Group select	BF element enables
0000		0x0000
0001		0x0180
0010		0x03C0
0011		0x07E0
0100		0x0FF0
0101		0x1FF8
0110		0x3FFC
0111		0x7FFE
1000		0xFFFF
1001		0x8001
1010		0xC003
1011		0xE007
1100		0xF00F
1101		0xF81F
1110		0xFC3F
1111		0xFE7F

Bits
31:28	Group select for state 0
27:24	Group select for state 1
23:20	Group select for state 2
19:16	Group select for state 3
15:12	Group select for state 4
11:8	Group select for state 5
7:4	Group select for state 6
3:0	Group select for state 7"""
