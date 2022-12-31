#include <stdint.h>

#include <iostream>

#include <tuple>

#pragma once

namespace rfdc {
  namespace cfg {
    enum class multiband_mode {
      SB = 0x0,
      BLK01_2X = 0x1,
      BLK23_2X = 0x2,
      ALL_2X = 0x3,
      ALL_4X = 0x4,
      ALT_2X = 0x5
    };
    
    struct dac_analog {
      uint32_t block_avail;
      uint32_t inv_sinc_en;
      uint32_t mix_mode;
      uint32_t decoder_mode;
    };

    struct dac_digital {
      uint32_t mixer_input_data_type;
      uint32_t data_width;
      uint32_t interpolation_mode;
      uint32_t fifo_enable;
      uint32_t adder_enable;
      uint32_t mixer_type;
    };

    struct dac {
      uint32_t enable;
      uint32_t pll_enable;
      double sample_rate;
      double ref_clk_freq;
      double fab_clk_freq;
      uint32_t feedback_div;
      uint32_t output_div;
      uint32_t ref_clk_div;
      uint32_t multiband;
      double max_sample_rate;
      uint32_t num_slices;
      uint32_t link_coupling;
      dac_analog analog[4];
      dac_digital digital[4];
    } __attribute__((packed));

    /*
      "C_ADC_Slice00_Enable"
      "C_ADC_Mixer_Mode00"
    */
    struct adc_analog {
      uint32_t block_avail;
      uint32_t mix_mode;
    };

    /*
      "C_ADC_Data_Type00"
      "C_ADC_Data_Width00"
      "C_ADC_Decimation_Mode00"
      "C_ADC_Fifo00_Enable"
      "C_ADC_Mixer_Type00"
    */
    struct adc_digital {
      uint32_t mixer_input_data_type;
      uint32_t data_width;
      uint32_t decimation_mode;
      uint32_t fifo_enable;
      uint32_t mixer_type;
    } __attribute__((packed));

    /*
      "C_ADC0_Enable"
      "C_ADC0_PLL_Enable"
      "C_ADC0_Sampling_Rate"
      "C_ADC0_Refclk_Freq"
      "C_ADC0_Fabric_Freq"
      "C_ADC0_FBDIV"								
      "C_ADC0_OutDiv"
      "C_ADC0_Refclk_Div"
      "C_ADC0_Band"
      "C_ADC0_Fs_Max"
      "C_ADC0_Slices"
    */

    struct adc {
      uint32_t enable;
      uint32_t pll_enable;
      double sample_rate;
      double ref_clk_freq;
      double fab_clk_freq;
      uint32_t feedback_div;
      uint32_t output_div;
      uint32_t ref_clk_div;
      uint32_t multiband;
      double max_sample_rate;
      uint32_t num_slices;
      adc_analog analog[4];
      adc_digital digital[4];
    } __attribute__((packed));

    /* 
       "DEVICE_ID" 
       "C_BASEADDR" 
       "C_High_Speed_ADC" 
       "C_Sysref_Master" 
       "C_Sysref_Master" 
       "C_Sysref_Source" 
       "C_Sysref_Source" 
       "C_IP_Type" 
       "C_Silicon_Revision"
    */
    struct dc {
      uint32_t device_id;
      uint64_t base_addr;
      uint32_t adc_type;
      uint32_t master_adc_tile;
      uint32_t master_dac_tile;
      uint32_t adc_sysref_source;
      uint32_t dac_sysref_source;
      uint32_t ip_type;
      uint32_t si_rev;
      dac dacs[4];
      adc adcs[4];
    } __attribute__((packed));

  };

  std::ostream &operator <<(std::ostream &os, const cfg::adc &);
  std::ostream &operator <<(std::ostream &os, const cfg::dac &);
  std::ostream &operator <<(std::ostream &os, const cfg::dc &);
};
