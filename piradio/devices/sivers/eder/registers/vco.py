from .register import Register
class vco:
    vco_en = Register(name="vco_en",addr=0xa0,size=0x1,mask=0x7f,default=0x0)
    vco_dig_tune = Register(name="vco_dig_tune",addr=0xa1,size=0x1,mask=0x7f,default=0x0)
    vco_ibias = Register(name="vco_ibias",addr=0xa2,size=0x1,mask=0x3f,default=0x0)
    vco_vtune_ctrl = Register(name="vco_vtune_ctrl",addr=0xa3,size=0x1,mask=0x33,default=0x0)
    vco_vtune_atc_lo_th = Register(name="vco_vtune_atc_lo_th",addr=0xa4,size=0x1,mask=0xff,default=0x0)
    vco_amux_ctrl = Register(name="vco_amux_ctrl",addr=0xa5,size=0x1,mask=0x1f,default=0x0)
    vco_vtune_th = Register(name="vco_vtune_th",addr=0xa6,size=0x1,mask=0xff,default=0x0)
    vco_atc_hi_th = Register(name="vco_atc_hi_th",addr=0xa7,size=0x1,mask=0xff,default=0x0)
    vco_atc_lo_th = Register(name="vco_atc_lo_th",addr=0xa8,size=0x1,mask=0xff,default=0x0)
    vco_alc_hi_th = Register(name="vco_alc_hi_th",addr=0xa9,size=0x1,mask=0xff,default=0x0)
    vco_override_ctrl = Register(name="vco_override_ctrl",addr=0xaa,size=0x2,mask=0x1ff,default=0x0)
    vco_alc_del = Register(name="vco_alc_del",addr=0xac,size=0x1,mask=0xff,default=0x0)
    vco_vtune_del = Register(name="vco_vtune_del",addr=0xad,size=0x1,mask=0xff,default=0x0)
    vco_tune_loop_del = Register(name="vco_tune_loop_del",addr=0xae,size=0x3,mask=0x3ffff,default=0x0)
    vco_atc_vtune_set_del = Register(name="vco_atc_vtune_set_del",addr=0xb1,size=0x3,mask=0x3ffff,default=0x0)
    vco_atc_vtune_unset_del = Register(name="vco_atc_vtune_unset_del",addr=0xb4,size=0x3,mask=0x3ffff,default=0x0)
    vco_tune_ctrl = Register(name="vco_tune_ctrl",addr=0xb7,size=0x1,mask=0x77,default=0x0)
    vco_tune_status = Register(name="vco_tune_status",addr=0xb8,size=0x1,mask=0xff,default=0x0)
    vco_tune_det_status = Register(name="vco_tune_det_status",addr=0xb9,size=0x1,mask=0xf,default=0x0)
    vco_tune_freq_cnt = Register(name="vco_tune_freq_cnt",addr=0xba,size=0x2,mask=0xfff,default=0x0)
    vco_tune_dig_tune = Register(name="vco_tune_dig_tune",addr=0xbc,size=0x1,mask=0x7f,default=0x40)
    vco_tune_ibias = Register(name="vco_tune_ibias",addr=0xbd,size=0x1,mask=0x3f,default=0x0)
    vco_tune_vtune = Register(name="vco_tune_vtune",addr=0xbe,size=0x1,mask=0xff,default=0x80)
    vco_tune_fd_polarity = Register(name="vco_tune_fd_polarity",addr=0xbf,size=0x1,mask=0x1,default=0x1)

    vco_en.doc = """VCO enable
Bits
0	External LO buffer in Enable
1	External LO buffer out Enable
2	PLL divider buffer out Enable
3	X3 buffer out Enable
4	VCO Enable
5	Comparator Enable
6	VCO Tune SM select (0=FD, 1=Vtune)"""
    vco_dig_tune.doc = """VCO Digital frequency tune override value
Bits 6:0 value
0x00	Min frequency
0x7F	Max frequency"""
    vco_ibias.doc = """VCO Amplitude setting override value

Note! Values above 0x1F not recommended, use with care

 Bits 5:0 value
0x00	Off
0x01	Min bias current
0x3F	Max bias frequency"""
    vco_vtune_ctrl.doc = """VCO Vtune setting
Bits
1:0	Vtune setting
4	Vtune Set
5	Vtune/ATC Low threshold mux func enable

Vtune setting
00	1.3 V
01	1.5 V
10	1.4 V
11	1.1 V"""
    vco_vtune_atc_lo_th.doc = """VCO Vtune setting for Vtune/ATC Low Threshold mux func"""
    vco_amux_ctrl.doc = """VCO Analog Mux Control
Bits
3:0	Amux Select
4	Amux Enable

Amux select
0	ALC Threshold
1	VCO Amplitude
2	ATC Low Threshold
3	ATC High Threshold
4	VCC VCO
5	VCC CHP
6	VCC Synth * 3/4
7	VCC TX BB * 3/4
8	VCC RX BB * 3/4"""
    vco_vtune_th.doc = """VCO Tune Vtune Threshold"""
    vco_atc_hi_th.doc = """VCO ATC High Threshold"""
    vco_atc_lo_th.doc = """VCO ATC Low Threshold"""
    vco_alc_hi_th.doc = """VCO ALC High Threshold"""
    vco_override_ctrl.doc = """VCO Override Control
Bits
0	External LO buffer in Enable override
1	External LO buffer out Enable override
2	PLL divider buffer out Enable override
3	X3 buffer out Enable override
4	VCO Enable override
5	VCO Comparator Enable override
6	VCO Vtune set override
7	VCO Digital tune override
8	VCO Ibias override"""
    vco_alc_del.doc = """VCO ALC Delay value"""
    vco_vtune_del.doc = """VCO Vtune Delay value"""
    vco_tune_loop_del.doc = """VCO Tune loop delay value
Bits
17:0	Delay value"""
    vco_atc_vtune_set_del.doc = """VCO ATC vtune set delay value
Bits
17:0	Delay value"""
    vco_atc_vtune_unset_del.doc = """VCO ATC vtune unset delay value
Bits
17:0	Delay value"""
    vco_tune_ctrl.doc = """VCO Automatic Tune Control
Start bit should be toggled, which can be achieved by writing 1 to bit 0 using SPI/SPB Bit toggle order.
Bits
0	Start
1	Reset
2	Retry
4	Start ALC SM
5	Start FD SM
6	Start Vtune SM"""
    vco_tune_status.doc = """VCO Automatic Tune Status. (Read only)
Bits
0	Main loop Done
1	Main loop Ok
2	ATC Done
3	ATC Ok
4	ALC Done
5	ALC Ok
6	FD Done
7	Vtune Done"""
    vco_tune_det_status.doc = """VCO Automatic Tune Detector  Status. (Read only)
Bits
0	PLL LD
1	ALC High Threshold
2	ATC Low Threshold
3	ATC High Threshold"""
    vco_tune_freq_cnt.doc = """VCO Tune Frequency Count. (Read only)
Bits
11:0	Frequency count value"""
    vco_tune_dig_tune.doc = """VCO Tune Digital tune value. (Read only)
Bits 6:0 value
0x00	Min frequency
0x7F	Max frequency"""
    vco_tune_ibias.doc = """VCO Tune Ibias value. (Read only)
Bits 5:0 value
0x00	Off
0x01	Min bias current
0x3F	Max bias frequency"""
    vco_tune_vtune.doc = """VCO Tune Vtune value (Read-only)"""
    vco_tune_fd_polarity.doc = """VCO Tune Frequency Detector polarity
Bits
0	0 = Negative polarity, 1 = Positive polarity"""
    vco_en.doc = """VCO enable
Bits
0	External LO buffer in Enable
1	External LO buffer out Enable
2	PLL divider buffer out Enable
3	X3 buffer out Enable
4	VCO Enable
5	Comparator Enable
6	VCO Tune SM select (0=FD, 1=Vtune)"""
    vco_dig_tune.doc = """VCO Digital frequency tune override value
Bits 6:0 value
0x00	Min frequency
0x7F	Max frequency"""
    vco_ibias.doc = """VCO Amplitude setting override value

Note! Values above 0x1F not recommended, use with care

 Bits 5:0 value
0x00	Off
0x01	Min bias current
0x3F	Max bias frequency"""
    vco_vtune_ctrl.doc = """VCO Vtune setting
Bits
1:0	Vtune setting
4	Vtune Set
5	Vtune/ATC Low threshold mux func enable

Vtune setting
00	1.3 V
01	1.5 V
10	1.4 V
11	1.1 V"""
    vco_vtune_atc_lo_th.doc = """VCO Vtune setting for Vtune/ATC Low Threshold mux func"""
    vco_amux_ctrl.doc = """VCO Analog Mux Control
Bits
3:0	Amux Select
4	Amux Enable

Amux select
0	ALC Threshold
1	VCO Amplitude
2	ATC Low Threshold
3	ATC High Threshold
4	VCC VCO
5	VCC CHP
6	VCC Synth * 3/4
7	VCC TX BB * 3/4
8	VCC RX BB * 3/4"""
    vco_vtune_th.doc = """VCO Tune Vtune Threshold"""
    vco_atc_hi_th.doc = """VCO ATC High Threshold"""
    vco_atc_lo_th.doc = """VCO ATC Low Threshold"""
    vco_alc_hi_th.doc = """VCO ALC High Threshold"""
    vco_override_ctrl.doc = """VCO Override Control
Bits
0	External LO buffer in Enable override
1	External LO buffer out Enable override
2	PLL divider buffer out Enable override
3	X3 buffer out Enable override
4	VCO Enable override
5	VCO Comparator Enable override
6	VCO Vtune set override
7	VCO Digital tune override
8	VCO Ibias override"""
    vco_alc_del.doc = """VCO ALC Delay value"""
    vco_vtune_del.doc = """VCO Vtune Delay value"""
    vco_tune_loop_del.doc = """VCO Tune loop delay value
Bits
17:0	Delay value"""
    vco_atc_vtune_set_del.doc = """VCO ATC vtune set delay value
Bits
17:0	Delay value"""
    vco_atc_vtune_unset_del.doc = """VCO ATC vtune unset delay value
Bits
17:0	Delay value"""
    vco_tune_ctrl.doc = """VCO Automatic Tune Control
Start bit should be toggled, which can be achieved by writing 1 to bit 0 using SPI/SPB Bit toggle order.
Bits
0	Start
1	Reset
2	Retry
4	Start ALC SM
5	Start FD SM
6	Start Vtune SM"""
    vco_tune_status.doc = """VCO Automatic Tune Status. (Read only)
Bits
0	Main loop Done
1	Main loop Ok
2	ATC Done
3	ATC Ok
4	ALC Done
5	ALC Ok
6	FD Done
7	Vtune Done"""
    vco_tune_det_status.doc = """VCO Automatic Tune Detector  Status. (Read only)
Bits
0	PLL LD
1	ALC High Threshold
2	ATC Low Threshold
3	ATC High Threshold"""
    vco_tune_freq_cnt.doc = """VCO Tune Frequency Count. (Read only)
Bits
11:0	Frequency count value"""
    vco_tune_dig_tune.doc = """VCO Tune Digital tune value. (Read only)
Bits 6:0 value
0x00	Min frequency
0x7F	Max frequency"""
    vco_tune_ibias.doc = """VCO Tune Ibias value. (Read only)
Bits 5:0 value
0x00	Off
0x01	Min bias current
0x3F	Max bias frequency"""
    vco_tune_vtune.doc = """VCO Tune Vtune value (Read-only)"""
    vco_tune_fd_polarity.doc = """VCO Tune Frequency Detector polarity
Bits
0	0 = Negative polarity, 1 = Positive polarity"""
