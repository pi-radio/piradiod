from .register import Register
class tx:
    tx_ctrl = Register(name="tx_ctrl",addr=0x60,size=0x1,mask=0x7f,default=0x10)
    tx_bb_q_dco = Register(name="tx_bb_q_dco",addr=0x61,size=0x1,mask=0x7f,default=0x40)
    tx_bb_i_dco = Register(name="tx_bb_i_dco",addr=0x62,size=0x1,mask=0x7f,default=0x40)
    tx_bb_phase = Register(name="tx_bb_phase",addr=0x63,size=0x1,mask=0x1f,default=0x0)
    tx_bb_gain = Register(name="tx_bb_gain",addr=0x64,size=0x1,mask=0x23,default=0x0)
    tx_bb_iq_gain = Register(name="tx_bb_iq_gain",addr=0x65,size=0x1,mask=0xff,default=0x0)
    tx_bfrf_gain = Register(name="tx_bfrf_gain",addr=0x66,size=0x1,mask=0xff,default=0x0)
    tx_bf_pdet_mux = Register(name="tx_bf_pdet_mux",addr=0x67,size=0x1,mask=0xbf,default=0x0)
    tx_alc_ctrl = Register(name="tx_alc_ctrl",addr=0x68,size=0x1,mask=0xf3,default=0x0)
    tx_alc_loop_cnt = Register(name="tx_alc_loop_cnt",addr=0x69,size=0x1,mask=0xff,default=0x0)
    tx_alc_start_delay = Register(name="tx_alc_start_delay",addr=0x6a,size=0x2,mask=0xffff,default=0x0)
    tx_alc_meas_delay = Register(name="tx_alc_meas_delay",addr=0x6c,size=0x1,mask=0xff,default=0x0)
    tx_alc_bfrf_gain_max = Register(name="tx_alc_bfrf_gain_max",addr=0x6d,size=0x1,mask=0xff,default=0xff)
    tx_alc_bfrf_gain_min = Register(name="tx_alc_bfrf_gain_min",addr=0x6e,size=0x1,mask=0xff,default=0x0)
    tx_alc_step_max = Register(name="tx_alc_step_max",addr=0x6f,size=0x1,mask=0x33,default=0x0)
    tx_alc_pdet_lo_th = Register(name="tx_alc_pdet_lo_th",addr=0x70,size=0x1,mask=0xff,default=0x0)
    tx_alc_pdet_hi_offs_th = Register(name="tx_alc_pdet_hi_offs_th",addr=0x71,size=0x1,mask=0x1f,default=0x0)
    tx_alc_bfrf_gain = Register(name="tx_alc_bfrf_gain",addr=0x72,size=0x1,mask=0xff,default=0x0)
    tx_alc_pdet = Register(name="tx_alc_pdet",addr=0x73,size=0x1,mask=0x3,default=0x0)

    tx_ctrl.doc = """TX control
Bits
0	BB I-channel Invert
1	BB Q-channel Invert
2	BB IQ Swap
3	BB Ibias Set
4	BB IQ Input common mode (0: 1.00 V, 1: 0.25 V)
5	TX Envelope detector enable
6	TX -> RX loop enable"""
    tx_bb_q_dco.doc = """TX BB Q-channel DC offset

Bits 6:0 value (Offset)

0x7F:	Max positive offset value
0x40:	No offset compensation
0x00:	Max negative offset value"""
    tx_bb_i_dco.doc = """TX BB I-channel DC offset

Bits 6:0 value (Offset)

0x7F:	Max positive offset value
0x40:	No offset compensation
0x00:	Max negative offset value"""
    tx_bb_phase.doc = """TX BB phase

Bits 4:0 value (Phase)

0x1F:	+15°
0x00:	0°"""
    tx_bb_gain.doc = """TX BB gain

tx_ctrl bit 3 (BB Ibias set) = 0
0x00  = 0 dB
0x01  = 6 dB
0x02  = 6 dB
0x03  = 9.5 dB

tx_ctrl bit 3 (BB Ibias set) = 1
0x00  = 0 dB
0x01  = 3.5 dB
0x02  = 3.5 dB
0x03  = 6 dB"""
    tx_bb_iq_gain.doc = """TX BB I- and Q-channel gain
Bits
3:0	I-channel gain -> Range: 0 - 6 dB / 0x0 - 0xF
7:4	Q-channel gain -> Range: 0 - 6 dB / 0x0 - 0xF"""
    tx_bfrf_gain.doc = """TX BF VGA and RF VGA gain settings (Max gain 15dB typical)

Bits 3:0 value(RF Gain)
0x0 = max gain – 15 dB
 ...
0xF = max gain

Bits 7:4 value (BF gain)
0x0 = max gain – 15 dB
...
0xF = max gain"""
    tx_bf_pdet_mux.doc = """TX BF Power Detector mux control
Bits
3:0	Power detector analog multiplexer
5:4	ALC analog multiplexer
7	Power detector Enable

ALC analog multiplexer
0x0:	Power detector
0x1:	ALC detector Hi threshold
0x2:	ALC detector Lo threshold
0x3:	dig tune

Power detector analog multiplexer
0x0:	TX0
0x1:	TX1
...
0xF:	TX15"""
    tx_alc_ctrl.doc = """TX ALC control
Bits
0	Enable ALC function
1	Start ALC (Toggle bit)
4	ALC temperature compensation enable
5	Adjust TX level during TX active
6	Adjust TX level during TX inactive
7	Adjust RF gain before BF gain"""
    tx_alc_loop_cnt.doc = """TX ALC loop count (7:0)
Sets number of times ALC is allowed to adjust gain"""
    tx_alc_start_delay.doc = """TX ALC start delay (15:0)

Sets delay from ALC trigger (run_once or TX becoming active)
until TX ALC detetctors are observed."""
    tx_alc_meas_delay.doc = """TX ALC measurement delay (7:0)

Sets delay from ALC gain change until TX ALC detetctors are observed again."""
    tx_alc_bfrf_gain_max.doc = """TX BF VGA and RF VGA max gain settings for ALC function

Bits 3:0 value(RF gain)
0x0 = max. gain - 15dB
 . . .
0xf = max. gain

Bits 7:4 value(BF gain)
0x0 = max. gain - 15dB
 . . .
0xf = max. gain"""
    tx_alc_bfrf_gain_min.doc = """TX BF VGA and RF VGA min gain settings for ALC function

Bits 3:0 value(RF Gain)
0x0 = max gain – 15 dB
...
0xF = max gain

Bits 7:4 value (BF gain)
0x0 = max gain – 15 dB
...
0xF = max gain"""
    tx_alc_step_max.doc = """TX BF VGA and RF VGA gain step max for ALC function

Bits 1:0:	RF gain step max
Bits 5:4:	BF gain step max"""
    tx_alc_pdet_lo_th.doc = """TX ALC power detector Lo Treshold (7:0)"""
    tx_alc_pdet_hi_offs_th.doc = """TX ALC power detector Hi Threshold offset from Lo Threshold (4:0)"""
    tx_alc_bfrf_gain.doc = """TX BF VGA and RF VGA gain set by ALC function (Read-only)"""
    tx_alc_pdet.doc = """TX ALC Power detector threshold flags (Read-only)

Bits:
0:	ALC Low indication
1:	ALC High indication"""
    tx_ctrl.doc = """TX control
Bits
0	BB I-channel Invert
1	BB Q-channel Invert
2	BB IQ Swap
3	BB Ibias Set
4	BB IQ Input common mode (0: 1.00 V, 1: 0.25 V)
5	TX Envelope detector enable
6	TX -> RX loop enable"""
    tx_bb_q_dco.doc = """TX BB Q-channel DC offset

Bits 6:0 value (Offset)

0x7F:	Max positive offset value
0x40:	No offset compensation
0x00:	Max negative offset value"""
    tx_bb_i_dco.doc = """TX BB I-channel DC offset

Bits 6:0 value (Offset)

0x7F:	Max positive offset value
0x40:	No offset compensation
0x00:	Max negative offset value"""
    tx_bb_phase.doc = """TX BB phase

Bits 4:0 value (Phase)

0x1F:	+15°
0x00:	0°"""
    tx_bb_gain.doc = """TX BB gain

tx_ctrl bit 3 (BB Ibias set) = 0
0x00  = 0 dB
0x01  = 6 dB
0x02  = 6 dB
0x03  = 9.5 dB

tx_ctrl bit 3 (BB Ibias set) = 1
0x00  = 0 dB
0x01  = 3.5 dB
0x02  = 3.5 dB
0x03  = 6 dB"""
    tx_bb_iq_gain.doc = """TX BB I- and Q-channel gain
Bits
3:0	I-channel gain -> Range: 0 - 6 dB / 0x0 - 0xF
7:4	Q-channel gain -> Range: 0 - 6 dB / 0x0 - 0xF"""
    tx_bfrf_gain.doc = """TX BF VGA and RF VGA gain settings (Max gain 15dB typical)

Bits 3:0 value(RF Gain)
0x0 = max gain – 15 dB
 ...
0xF = max gain

Bits 7:4 value (BF gain)
0x0 = max gain – 15 dB
...
0xF = max gain"""
    tx_bf_pdet_mux.doc = """TX BF Power Detector mux control
Bits
3:0	Power detector analog multiplexer
5:4	ALC analog multiplexer
7	Power detector Enable

ALC analog multiplexer
0x0:	Power detector
0x1:	ALC detector Hi threshold
0x2:	ALC detector Lo threshold
0x3:	dig tune

Power detector analog multiplexer
0x0:	TX0
0x1:	TX1
...
0xF:	TX15"""
    tx_alc_ctrl.doc = """TX ALC control
Bits
0	Enable ALC function
1	Start ALC (Toggle bit)
4	ALC temperature compensation enable
5	Adjust TX level during TX active
6	Adjust TX level during TX inactive
7	Adjust RF gain before BF gain"""
    tx_alc_loop_cnt.doc = """TX ALC loop count (7:0)
Sets number of times ALC is allowed to adjust gain"""
    tx_alc_start_delay.doc = """TX ALC start delay (15:0)

Sets delay from ALC trigger (run_once or TX becoming active)
until TX ALC detetctors are observed."""
    tx_alc_meas_delay.doc = """TX ALC measurement delay (7:0)

Sets delay from ALC gain change until TX ALC detetctors are observed again."""
    tx_alc_bfrf_gain_max.doc = """TX BF VGA and RF VGA max gain settings for ALC function

Bits 3:0 value(RF gain)
0x0 = max. gain - 15dB
 . . .
0xf = max. gain

Bits 7:4 value(BF gain)
0x0 = max. gain - 15dB
 . . .
0xf = max. gain"""
    tx_alc_bfrf_gain_min.doc = """TX BF VGA and RF VGA min gain settings for ALC function

Bits 3:0 value(RF Gain)
0x0 = max gain – 15 dB
...
0xF = max gain

Bits 7:4 value (BF gain)
0x0 = max gain – 15 dB
...
0xF = max gain"""
    tx_alc_step_max.doc = """TX BF VGA and RF VGA gain step max for ALC function

Bits 1:0:	RF gain step max
Bits 5:4:	BF gain step max"""
    tx_alc_pdet_lo_th.doc = """TX ALC power detector Lo Treshold (7:0)"""
    tx_alc_pdet_hi_offs_th.doc = """TX ALC power detector Hi Threshold offset from Lo Threshold (4:0)"""
    tx_alc_bfrf_gain.doc = """TX BF VGA and RF VGA gain set by ALC function (Read-only)"""
    tx_alc_pdet.doc = """TX ALC Power detector threshold flags (Read-only)

Bits:
0:	ALC Low indication
1:	ALC High indication"""
