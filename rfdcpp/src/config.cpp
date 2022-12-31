#include <xrfdcpp/config.hpp>
#include <xrfdcpp/regs.hpp>

namespace rfdc {
  std::ostream &operator <<(std::ostream &os, const cfg::adc_analog &aa)
  {
    os << "  avail: " << aa.block_avail << std::endl
       << "  mix mode: " << aa.mix_mode << std::endl
      ;

    return os;
  }

  
  std::ostream &operator <<(std::ostream &os, const cfg::adc_digital &ad)
  {
    os << "  input data: " << ad.mixer_input_data_type << std::endl
       << "  data width: " << ad.data_width << std::endl
       << "  decimation mode: " << ad.decimation_mode << std::endl
       << "  fifo enable: " << ad.fifo_enable << std::endl
       << "  mixer type: " << ad.mixer_type << std::endl
      ;

    return os;
  }
  
  std::ostream &operator <<(std::ostream &os, const cfg::adc &adc)
  {
    os << " enabled: " << adc.enable << std::endl
       << " pll enabled: " << adc.pll_enable << std::endl
       << " sample rate: " << adc.sample_rate << std::endl
       << " reference clock: " << adc.ref_clk_freq << std::endl
       << " fabric clock: " << adc.fab_clk_freq << std::endl
       << " feedback divider: " << adc.feedback_div << std::endl
       << " output divider: " << adc.output_div << std::endl
       << " reference clock divider: " << adc.ref_clk_div << std::endl
       << " multiband: " << adc.multiband << std::endl
       << " max sample rate: " << adc.max_sample_rate << std::endl
       << " num slices: " << adc.num_slices << std::endl
      ;

    for (int i = 0; i < 4; i++) {
      std::cout << " ADC Slice Entry " << i << std::endl;
      os << adc.analog[i];
      os << adc.digital[i];
    }
    
    return os;
  }
  
  std::ostream &operator <<(std::ostream &os, const cfg::dac &dac)
  {
    os << " enabled: " << dac.enable << std::endl
       << " pll enabled: " << dac.pll_enable << std::endl
       << " sample rate: " << dac.sample_rate << std::endl
       << " reference clock: " << dac.ref_clk_freq << std::endl
       << " fabric clock: " << dac.fab_clk_freq << std::endl
       << " feedback divider: " << dac.feedback_div << std::endl
       << " output divider: " << dac.output_div << std::endl
       << " reference clock divider: " << dac.ref_clk_div << std::endl
       << " multiband: " << dac.multiband << std::endl
       << " max sample rate: " << dac.max_sample_rate << std::endl
       << " num slices: " << dac.num_slices << std::endl
      ;

    return os;
  }
  
  std::ostream &operator <<(std::ostream &os, const cfg::dc &dc)
  {
    os << "Device id: " << dc.device_id << std::endl
       << "Base addr: " << std::hex << dc.base_addr << std::dec << std::endl
       << "ADC type: " << dc.adc_type << std::endl
       << "Master ADC: " << dc.master_adc_tile << std::endl
       << "Master DAC: " << dc.master_dac_tile << std::endl
       << "ADC Sysref Source: " << dc.adc_sysref_source << std::endl
       << "DAC Sysref Source: " << dc.dac_sysref_source << std::endl
       << "IP Type: " << dc.ip_type << std::endl
       << "Silicon Rev: " << dc.si_rev << std::endl
      ;

    for (int i = 0; i < 4; i++) {
      os << "DAC " << i << std::endl;
      os << dc.dacs[i];
    }
  
    for (int i = 0; i < 4; i++) {
      os << "ADC " << i << std::endl;
      os << dc.adcs[i];
    }
  
    return os;
  }
};
