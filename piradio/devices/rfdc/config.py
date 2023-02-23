import inspect

from piradio.newstruct import newstruct, u32, double, addr

    

@newstruct
class TileConfig:
    enable: u32
    pll_enable: u32
    sampling_rate: double
    ref_clk_freq: double
    fab_clk_freq: double
    feedback_div: u32
    output_div: u32
    refclk_div: u32
    multiband_cfg: u32
    max_sample_rate: double
    slices: u32
        
@newstruct
class DACDigitalPathConfig:
    mixer_input_data_type: u32
    data_width: u32
    interpolation_mode: u32
    fifo_enable: u32
    adder_enable: u32
    mixer_type: u32
    
@newstruct
class DACAnalogPathConfig:
    available: u32
    inv_sinc_enable: u32
    mix_mode: u32
    decoder_mode: u32
    
@newstruct
class DACTileConfig(TileConfig):
    link_coupling: u32
    analog: DACAnalogPathConfig[4]
    digital: DACDigitalPathConfig[4]
        
@newstruct
class ADCDigitalPathConfig:
    mixer_input_data_type: u32
    data_width: u32
    decimation_mode: u32
    fifo_enable: u32
    mixer_type: u32
    
@newstruct
class ADCAnalogPathConfig:
    available: u32
    mix_mode: u32
    
@newstruct
class ADCTileConfig(TileConfig):
    analog: ADCAnalogPathConfig[4]
    digital: ADCDigitalPathConfig[4]
            
@newstruct
class RFDCConfigParams:
    device_type: u32
    address: addr
    adc_type: u32
    master_adc: u32
    master_dac: u32
    adc_sysref_src: u32
    dac_sysref_src: u32
    ip_type: u32
    silicon_rev: u32
    DAC: DACTileConfig[4]
    ADC: ADCTileConfig[4]
