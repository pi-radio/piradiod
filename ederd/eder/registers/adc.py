from .register import Register
class adc:
    adc_ctrl = Register(name="adc_ctrl",addr=0x80,size=0x1,mask=0xb7,default=0x0)
    adc_clk_div = Register(name="adc_clk_div",addr=0x81,size=0x1,mask=0xff,default=0x3)
    adc_sample_cycle = Register(name="adc_sample_cycle",addr=0x82,size=0x1,mask=0x3f,default=0x0)
    adc_num_samples = Register(name="adc_num_samples",addr=0x83,size=0x1,mask=0xf,default=0x0)
    adc_sample = Register(name="adc_sample",addr=0x90,size=0x2,mask=0xfff,default=0x0)
    adc_mean = Register(name="adc_mean",addr=0x92,size=0x2,mask=0xfff,default=0x0)
    adc_max = Register(name="adc_max",addr=0x94,size=0x2,mask=0xfff,default=0x0)
    adc_min = Register(name="adc_min",addr=0x96,size=0x2,mask=0xfff,default=0x0)
    adc_diff = Register(name="adc_diff",addr=0x98,size=0x2,mask=0x1fff,default=0x0)

    adc_ctrl.doc = """ADC Control
Bits
0:	Enable analogue part of ADC (Override automatic)
1:	Clock edge (1=Rising, 0= Falling)
2:	Continuous
4:	Start (Toggle)
5:	Reset (Toggle)
7:	Ready (Read-only)"""
    adc_clk_div.doc = """ADC clock division factor
ADC sample clock = fast_clk / 38*(adc_clk_div+1)
ADC state machine clock = fast_clk / (adc_clk_div+1)
Bits
7:0	ADC clock division factor"""
    adc_sample_cycle.doc = """ADC sample cycle
Valid values : 0-37
Bits
5:0	ADC sample cycle"""
    adc_num_samples.doc = """ADC Log2 of number of samples
Valid values : 0-10
Number of samples = 2^adc_num_samples
Bits
3:0	Log2 of Number of samples"""
    adc_sample.doc = """ADC sample
Bits
11:0	ADC sample value"""
    adc_mean.doc = """ADC mean of Num of samples
Bits
11:0	ADC sample value"""
    adc_max.doc = """ADC max among Num of samples
Bits
11:0	ADC sample value"""
    adc_min.doc = """ADC min among Num of samples
Bits
11:0	ADC sample value"""
    adc_diff.doc = """ADC sample diff (difference between current value and previous)
Bits
12:0	ADC sample value"""
    adc_ctrl.doc = """ADC Control
Bits
0:	Enable analogue part of ADC (Override automatic)
1:	Clock edge (1=Rising, 0= Falling)
2:	Continuous
4:	Start (Toggle)
5:	Reset (Toggle)
7:	Ready (Read-only)"""
    adc_clk_div.doc = """ADC clock division factor
ADC sample clock = fast_clk / 38*(adc_clk_div+1)
ADC state machine clock = fast_clk / (adc_clk_div+1)
Bits
7:0	ADC clock division factor"""
    adc_sample_cycle.doc = """ADC sample cycle
Valid values : 0-37
Bits
5:0	ADC sample cycle"""
    adc_num_samples.doc = """ADC Log2 of number of samples
Valid values : 0-10
Number of samples = 2^adc_num_samples
Bits
3:0	Log2 of Number of samples"""
    adc_sample.doc = """ADC sample
Bits
11:0	ADC sample value"""
    adc_mean.doc = """ADC mean of Num of samples
Bits
11:0	ADC sample value"""
    adc_max.doc = """ADC max among Num of samples
Bits
11:0	ADC sample value"""
    adc_min.doc = """ADC min among Num of samples
Bits
11:0	ADC sample value"""
    adc_diff.doc = """ADC sample diff (difference between current value and previous)
Bits
12:0	ADC sample value"""
