from .register import Register
class agc:
    agc_int_ctrl = Register(name="agc_int_ctrl",addr=0xe0,size=0x1,mask=0x3,default=0x0)
    agc_int_en_ctrl = Register(name="agc_int_en_ctrl",addr=0xe1,size=0x1,mask=0x1f,default=0x20)
    agc_int_backoff = Register(name="agc_int_backoff",addr=0xe2,size=0x1,mask=0xff,default=0x0)
    agc_int_start_del = Register(name="agc_int_start_del",addr=0xe3,size=0x1,mask=0xff,default=0x0)
    agc_int_timeout = Register(name="agc_int_timeout",addr=0xe4,size=0x1,mask=0xff,default=0x0)
    agc_int_gain_change_del = Register(name="agc_int_gain_change_del",addr=0xe5,size=0x1,mask=0xf,default=0x5)
    agc_int_pdet_en = Register(name="agc_int_pdet_en",addr=0xe6,size=0x1,mask=0xf,default=0x9)
    agc_int_pdet_filt = Register(name="agc_int_pdet_filt",addr=0xe7,size=0x2,mask=0x1fff,default=0x1f1f)
    agc_int_pdet_th = Register(name="agc_int_pdet_th",addr=0xe9,size=0x5,mask=0xffffffffff,default=0x0)
    agc_int_bfrf_gain_lvl = Register(name="agc_int_bfrf_gain_lvl",addr=0xee,size=0x4,mask=0xffffffff,default=0xffcc9966)
    agc_int_bb3_gain_lvl = Register(name="agc_int_bb3_gain_lvl",addr=0xf2,size=0x3,mask=0xffffff,default=0xfca752)
    agc_int_status_pdet = Register(name="agc_int_status_pdet",addr=0xf5,size=0x2,mask=0x1fff,default=0xf4)
    agc_int_status = Register(name="agc_int_status",addr=0xf7,size=0x1,mask=0x3,default=0x0)
    agc_int_gain = Register(name="agc_int_gain",addr=0xf8,size=0x1,mask=0xff,default=0x0)
    agc_int_gain_setting = Register(name="agc_int_gain_setting",addr=0xf9,size=0x4,mask=0xffffffff,default=0xffffffff)
    agc_ext_ctrl = Register(name="agc_ext_ctrl",addr=0xfd,size=0x1,mask=0x7,default=0x5)

    agc_int_ctrl.doc = """Internal AGC Control (Toggle register)
Start and Reset bits should be toggled, which can be achieved 
by writing 1 to corresponding bit using SPI/SPB Bit toggle order.
These are optional controls to the direct controls via GPIO:s
Bits 1:0
0	Start
1	Reset"""
    agc_int_en_ctrl.doc = """Internal AGC Enable
Bits 4:0
0	BFRF and BB gain adjust separation enable
1	Start delay timer enable
2	Timeout timer enable
3	AGC backoff enable
4	Wait for detection trigger"""
    agc_int_backoff.doc = """Internal AGC Backoff setting
Bits 7:0
7:0	AGC Backoff (in dB)"""
    agc_int_start_del.doc = """Internal AGC Start Delay (7:0)"""
    agc_int_timeout.doc = """Internal AGC Timeout (7:0)"""
    agc_int_gain_change_del.doc = """Internal AGC Gain Change Duration (3:0)"""
    agc_int_pdet_en.doc = """Internal AGC Power Detector Enable

Bits 3:0
3:2	Detector Reset Control
1	Outband Power Detector Enable
0	BFRF, BB VGA1, VGA2 and VGA3 Power Detector Enable

Detector Reset Control
00	Detector reset inactive
01	Detector controlled by AGC (1 cycle long)
10	Detector controlled by AGC (2 cycles long)
11	Detector reset active"""
    agc_int_pdet_filt.doc = """Internal AGC Power Detector Filter
Bits 12:0
4:0	Power Detector mask for I-channel
12:8	Power Detector mask for Q-channel"""
    agc_int_pdet_th.doc = """Internal AGC Power Detector Thresholds
Bits 39:0
39:32	Outband Power Detector Threshold
31:24	BFRF VGAs Power Detector Threshold
39:16	BB VGA1 Power Detector Threshold
15:8	BB VGA2 Power Detector Threshold
7:0	BB VGA3 Power Detector Threshold"""
    agc_int_bfrf_gain_lvl.doc = """Internal AGC BF and RF Gain Level settings
Bits 31:0
3:0	RF gain setting 0 dB
7:4	BF gain setting 0 dB
11:8	RF gain setting 6 dB
15:12	BF gain setting 6 dB
19:16	RF gain setting 12 dB
23:20	BF gain setting 12 dB
27:24	RF gain setting 18 dB
31:28	BF gain setting 18 dB"""
    agc_int_bb3_gain_lvl.doc = """AGC BB VGA3 Gain Level settings
Bits 23:0
3:0	BB VGA3 Gain setting 0 dB
7:4	BB VGA3 Gain setting 1 dB
11:8	BB VGA3 Gain setting 2 dB
15:12	BB VGA3 Gain setting 3 dB
19:16	BB VGA3 Gain setting 4 dB
23:20	BB VGA3 Gain setting 5 dB"""
    agc_int_status_pdet.doc = """Internal AGC Detector Status (Read only)
Bits 12:0
4:0	I-channel detector status
12:8	Q-channel detector status"""
    agc_int_status.doc = """Internal AGC Status (Read only)
Bits 1:0
0	AGC Done
1	AGC Timeout"""
    agc_int_gain.doc = """Internal AGC Gain (Read only)"""
    agc_int_gain_setting.doc = """Internal AGC Gain Setting (Read only)
Bits 31:0
3:0	BB VGA3 Gain setting I-channel
7:4	BB VGA3 Gain setting Q-channel
11:8	BB VGA2 Gain setting I-channel
15:12	BB VGA2 Gain setting Q-channel
19:16	BB VGA1 Gain setting I-channel
23:20	BB VGA1 Gain setting Q-channel
27:24	RF Gain setting
31:28	BF Gain setting"""
    agc_ext_ctrl.doc = """External AGC Control
Bits 2:0
2	Enable DDR mode (1=DDR, 0=SDR)
1	SDR sample edge (1= rising, 0=falling)
0	Align Index update to last falling edge"""
    agc_int_ctrl.doc = """Internal AGC Control (Toggle register)
Start and Reset bits should be toggled, which can be achieved 
by writing 1 to corresponding bit using SPI/SPB Bit toggle order.
These are optional controls to the direct controls via GPIO:s
Bits 1:0
0	Start
1	Reset"""
    agc_int_en_ctrl.doc = """Internal AGC Enable
Bits 4:0
0	BFRF and BB gain adjust separation enable
1	Start delay timer enable
2	Timeout timer enable
3	AGC backoff enable
4	Wait for detection trigger"""
    agc_int_backoff.doc = """Internal AGC Backoff setting
Bits 7:0
7:0	AGC Backoff (in dB)"""
    agc_int_start_del.doc = """Internal AGC Start Delay (7:0)"""
    agc_int_timeout.doc = """Internal AGC Timeout (7:0)"""
    agc_int_gain_change_del.doc = """Internal AGC Gain Change Duration (3:0)"""
    agc_int_pdet_en.doc = """Internal AGC Power Detector Enable

Bits 3:0
3:2	Detector Reset Control
1	Outband Power Detector Enable
0	BFRF, BB VGA1, VGA2 and VGA3 Power Detector Enable

Detector Reset Control
00	Detector reset inactive
01	Detector controlled by AGC (1 cycle long)
10	Detector controlled by AGC (2 cycles long)
11	Detector reset active"""
    agc_int_pdet_filt.doc = """Internal AGC Power Detector Filter
Bits 12:0
4:0	Power Detector mask for I-channel
12:8	Power Detector mask for Q-channel"""
    agc_int_pdet_th.doc = """Internal AGC Power Detector Thresholds
Bits 39:0
39:32	Outband Power Detector Threshold
31:24	BFRF VGAs Power Detector Threshold
39:16	BB VGA1 Power Detector Threshold
15:8	BB VGA2 Power Detector Threshold
7:0	BB VGA3 Power Detector Threshold"""
    agc_int_bfrf_gain_lvl.doc = """Internal AGC BF and RF Gain Level settings
Bits 31:0
3:0	RF gain setting 0 dB
7:4	BF gain setting 0 dB
11:8	RF gain setting 6 dB
15:12	BF gain setting 6 dB
19:16	RF gain setting 12 dB
23:20	BF gain setting 12 dB
27:24	RF gain setting 18 dB
31:28	BF gain setting 18 dB"""
    agc_int_bb3_gain_lvl.doc = """AGC BB VGA3 Gain Level settings
Bits 23:0
3:0	BB VGA3 Gain setting 0 dB
7:4	BB VGA3 Gain setting 1 dB
11:8	BB VGA3 Gain setting 2 dB
15:12	BB VGA3 Gain setting 3 dB
19:16	BB VGA3 Gain setting 4 dB
23:20	BB VGA3 Gain setting 5 dB"""
    agc_int_status_pdet.doc = """Internal AGC Detector Status (Read only)
Bits 12:0
4:0	I-channel detector status
12:8	Q-channel detector status"""
    agc_int_status.doc = """Internal AGC Status (Read only)
Bits 1:0
0	AGC Done
1	AGC Timeout"""
    agc_int_gain.doc = """Internal AGC Gain (Read only)"""
    agc_int_gain_setting.doc = """Internal AGC Gain Setting (Read only)
Bits 31:0
3:0	BB VGA3 Gain setting I-channel
7:4	BB VGA3 Gain setting Q-channel
11:8	BB VGA2 Gain setting I-channel
15:12	BB VGA2 Gain setting Q-channel
19:16	BB VGA1 Gain setting I-channel
23:20	BB VGA1 Gain setting Q-channel
27:24	RF Gain setting
31:28	BF Gain setting"""
    agc_ext_ctrl.doc = """External AGC Control
Bits 2:0
2	Enable DDR mode (1=DDR, 0=SDR)
1	SDR sample edge (1= rising, 0=falling)
0	Align Index update to last falling edge"""
