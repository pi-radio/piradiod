from .register import Register
class rx:
    rx_gain_ctrl_mode = Register(name="rx_gain_ctrl_mode",addr=0xc0,size=0x1,mask=0x3b,default=0x0)
    rx_gain_ctrl_reg_index = Register(name="rx_gain_ctrl_reg_index",addr=0xc1,size=0x1,mask=0xff,default=0x0)
    rx_gain_ctrl_sel = Register(name="rx_gain_ctrl_sel",addr=0xc2,size=0x2,mask=0x3ff,default=0x0)
    rx_gain_ctrl_bfrf = Register(name="rx_gain_ctrl_bfrf",addr=0xc4,size=0x1,mask=0xff,default=0x0)
    rx_gain_ctrl_bb1 = Register(name="rx_gain_ctrl_bb1",addr=0xc5,size=0x1,mask=0xff,default=0x0)
    rx_gain_ctrl_bb2 = Register(name="rx_gain_ctrl_bb2",addr=0xc6,size=0x1,mask=0xff,default=0x0)
    rx_gain_ctrl_bb3 = Register(name="rx_gain_ctrl_bb3",addr=0xc7,size=0x1,mask=0xff,default=0x0)
    rx_bb_q_dco = Register(name="rx_bb_q_dco",addr=0xc8,size=0x2,mask=0x3fff,default=0x40)
    rx_bb_i_dco = Register(name="rx_bb_i_dco",addr=0xca,size=0x2,mask=0x3fff,default=0x40)
    rx_dco_en = Register(name="rx_dco_en",addr=0xcc,size=0x1,mask=0x1,default=0x0)
    rx_bb_biastrim = Register(name="rx_bb_biastrim",addr=0xcd,size=0x1,mask=0x3f,default=0x0)
    rx_bb_test_ctrl = Register(name="rx_bb_test_ctrl",addr=0xce,size=0x1,mask=0xff,default=0x0)
    rx_drv_dco = Register(name="rx_drv_dco",addr=0x1c,size=0x4,mask=0xffffffff,default=0xff0000ff)

    rx_gain_ctrl_mode.doc = """RX Gain Control Mode
Gain Control Mode
00	External AGC control
01	Internal AGC control
10	Register Index control
11	Register Direct control

Bits
1:0	Gain Control mode
3	1 = Leave selects in rx_gain_ctrl_sel untouched.
	0 = Set selects in rx_gain_ctrl_sel to same value as written.(Bit is auto-cleared)
4	Store AGC value in AWV Table
5	Use AGC value from AWV Table during Internal AGC Idle state"""
    rx_gain_ctrl_reg_index.doc = """RX Gain Control by Index"""
    rx_gain_ctrl_sel.doc = """RX Gain Control Select
Gain Control Mode
00	External AGC control
01	Internal AGC control
10	Register Index control
11	Register Direct control
Bits

9:8	Gain Control mode for BF VGA gain
7:6	Gain Control mode for RF VGA gain
5:4	Gain Control mode for BB VGA1 gain
3:2	Gain Control mode for BB VGA2 gain
1:0	Gain Control mode for BB VGA3 gain"""
    rx_gain_ctrl_bfrf.doc = """RX BF VGA and RF VGA gain settings (Max gain 15dB typical)
Bits 3:0 value (RF Gain)
0x0 = max gain – 15 dB
...
0xF = max gain

Bits 7:4 value(BF Gain)
0x0 = max gain – 15 dB
...
0xF = max gain"""
    rx_gain_ctrl_bb1.doc = """RX BB VGA1 gain setting for Q- and I-channel
Bits
3:0	VGA1 I-channel
7:4	VGA1 Q-channel
Allowed values per channel: 0xF, 0x7, 0x3, 0x1, 0x0,
where 0xF is the highest gain and then the gain drops by 6 db per step down to the setting 0x0."""
    rx_gain_ctrl_bb2.doc = """RX BB VGA2 gain setting for Q- and I-channel
Bits
3:0	VGA2 I-channel
7:4	VGA2 Q-channel
Allowed values per channel: 0xF, 0x7, 0x3, 0x1, 0x0,
where 0xF is the highest gain and then the gain drops by 6 db per step down to the setting 0x0"""
    rx_gain_ctrl_bb3.doc = """RX BB VGA3 gain setting for Q- and I-channel
Bits
3:0	VGA3 I-channel
7:4	VGA3 Q-channel
Range 0 - 0xF : 0 - 6 dB"""
    rx_bb_q_dco.doc = """RX BB Q-channel DC Offset
Bits 6:0 value(Offset)
0x7F:	Max positive offset value
0x40:	No offset compensation
0x00:	Max negative offset value

Bits 9:8 value (Offset shift)
00:	No shift
01:	Negative shift (by 87% of offset value range)
10:	Positive shift (by 87% of offset value range)
11:	Not used

Bits 13:12 value (Multiplication factor on Offset value)
00:	x1
01:	x2
10:	x3
11:	x4"""
    rx_bb_i_dco.doc = """RX BB I-channel DC Offset
Bits 6:0 value(Offset)
0x7F:	Max positive offset value
0x40:	No offset compensation
0x00:	Max negative offset value

Bits 9:8 value (Offset shift)
00:	No shift
01:	Negative shift (by 87% of offset value range)
10:	Positive shift (by 87% of offset value range)
11:	Not used

Bits 13:12 value (Multiplication factor on Offset value)
00:	x1
01:	x2
10:	x3
11:	x4"""
    rx_dco_en.doc = """RX DCO Enable
Bits
0:	enable DC Offset compensation"""
    rx_bb_biastrim.doc = """Fine trim bias for BB VGA1, VGA2

Bits 2:0 value(VGA1)
000	Nominal bias current
001	-4% bias current
...
111	-28% bias current

Bits 5:3 value (VGA2)
000	Nominal bias current
001	-4% bias current
...
111	-28% bias current"""
    rx_bb_test_ctrl.doc = """RX BB Test Control
Bits
1:0	I/Q select
3:2	Parameter select
6:4	Source select
7:	Enable BB_RX AMUX

I/Q select
00	Unused
01	I-channel
10	Q-channel
11	Unused

Parameter select
00	Power Detector (For VGA3; voltage on output current node, for CM measurement)
01	Power Detector Threshold (For VGA3; voltage on output current node, for CM measurement)
10	DC-level P
11	DC-level N

Source select
000	Out-of-band detector
001	Input buffer
010	VGA1
011	VGA2
100	VGA3
101	Output buffer
110	Unused
111	Unused"""
    rx_gain_ctrl_mode.doc = """RX Gain Control Mode
Gain Control Mode
00	External AGC control
01	Internal AGC control
10	Register Index control
11	Register Direct control

Bits
1:0	Gain Control mode
3	1 = Leave selects in rx_gain_ctrl_sel untouched.
	0 = Set selects in rx_gain_ctrl_sel to same value as written.(Bit is auto-cleared)
4	Store AGC value in AWV Table
5	Use AGC value from AWV Table during Internal AGC Idle state"""
    rx_gain_ctrl_reg_index.doc = """RX Gain Control by Index"""
    rx_gain_ctrl_sel.doc = """RX Gain Control Select
Gain Control Mode
00	External AGC control
01	Internal AGC control
10	Register Index control
11	Register Direct control
Bits

9:8	Gain Control mode for BF VGA gain
7:6	Gain Control mode for RF VGA gain
5:4	Gain Control mode for BB VGA1 gain
3:2	Gain Control mode for BB VGA2 gain
1:0	Gain Control mode for BB VGA3 gain"""
    rx_gain_ctrl_bfrf.doc = """RX BF VGA and RF VGA gain settings (Max gain 15dB typical)
Bits 3:0 value (RF Gain)
0x0 = max gain – 15 dB
...
0xF = max gain

Bits 7:4 value(BF Gain)
0x0 = max gain – 15 dB
...
0xF = max gain"""
    rx_gain_ctrl_bb1.doc = """RX BB VGA1 gain setting for Q- and I-channel
Bits
3:0	VGA1 I-channel
7:4	VGA1 Q-channel
Allowed values per channel: 0xF, 0x7, 0x3, 0x1, 0x0,
where 0xF is the highest gain and then the gain drops by 6 db per step down to the setting 0x0."""
    rx_gain_ctrl_bb2.doc = """RX BB VGA2 gain setting for Q- and I-channel
Bits
3:0	VGA2 I-channel
7:4	VGA2 Q-channel
Allowed values per channel: 0xF, 0x7, 0x3, 0x1, 0x0,
where 0xF is the highest gain and then the gain drops by 6 db per step down to the setting 0x0"""
    rx_gain_ctrl_bb3.doc = """RX BB VGA3 gain setting for Q- and I-channel
Bits
3:0	VGA3 I-channel
7:4	VGA3 Q-channel
Range 0 - 0xF : 0 - 6 dB"""
    rx_bb_q_dco.doc = """RX BB Q-channel DC Offset
Bits 6:0 value(Offset)
0x7F:	Max positive offset value
0x40:	No offset compensation
0x00:	Max negative offset value

Bits 9:8 value (Offset shift)
00:	No shift
01:	Negative shift (by 87% of offset value range)
10:	Positive shift (by 87% of offset value range)
11:	Not used

Bits 13:12 value (Multiplication factor on Offset value)
00:	x1
01:	x2
10:	x3
11:	x4"""
    rx_bb_i_dco.doc = """RX BB I-channel DC Offset
Bits 6:0 value(Offset)
0x7F:	Max positive offset value
0x40:	No offset compensation
0x00:	Max negative offset value

Bits 9:8 value (Offset shift)
00:	No shift
01:	Negative shift (by 87% of offset value range)
10:	Positive shift (by 87% of offset value range)
11:	Not used

Bits 13:12 value (Multiplication factor on Offset value)
00:	x1
01:	x2
10:	x3
11:	x4"""
    rx_dco_en.doc = """RX DCO Enable
Bits
0:	enable DC Offset compensation"""
    rx_drv_dco.doc = """RX DCO Drive control

Bit 0:		1=Enabled LNAs   0=Disabled LNAs
Bits 12:8:		Driver dco offset for BB_Q.
Bit 13:		1=BB_Q Positive offset   0=BB_Q Negative offset
Bits 18:14:	Driver dco offset for BB_I.
Bit 19:		1=BB_I Positive offset   0=BB_I Negative offset"""
    rx_bb_biastrim.doc = """Fine trim bias for BB VGA1, VGA2

Bits 2:0 value(VGA1)
000	Nominal bias current
001	-4% bias current
...
111	-28% bias current

Bits 5:3 value (VGA2)
000	Nominal bias current
001	-4% bias current
...
111	-28% bias current"""
    rx_bb_test_ctrl.doc = """RX BB Test Control
Bits
1:0	I/Q select
3:2	Parameter select
6:4	Source select
7:	Enable BB_RX AMUX

I/Q select
00	Unused
01	I-channel
10	Q-channel
11	Unused

Parameter select
00	Power Detector (For VGA3; voltage on output current node, for CM measurement)
01	Power Detector Threshold (For VGA3; voltage on output current node, for CM measurement)
10	DC-level P
11	DC-level N

Source select
000	Out-of-band detector
001	Input buffer
010	VGA1
011	VGA2
100	VGA3
101	Output buffer
110	Unused
111	Unused"""
