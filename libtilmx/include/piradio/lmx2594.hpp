#pragma once

#include <piradio/freq_module.hpp>
#include <piradio/lmx2594_config.hpp>

namespace piradio
{
  class LMX2594
  {
  public:
    LMX2594Config config;

    frequency    sysref_freq;
    
    frequency    f_osc_in;
    freq_source  osc_in;
  
    freq_mod     osc_2x;
    freq_mod     osc_pre_div;
    freq_mod     osc_mult;
    freq_mod     osc_post_div;
    freq_mod     VCO;
    freq_mod     channel_divider;

    struct mux_select {
      enum {
	CHANNEL_DIVIDER = 0,
	VCO = 1,
	SYSREF = 2,
	HIZ = 3
      };
    };
    
    LMX2594(const frequency &_f_osc_in, uint8_t A_pwr = 12, uint8_t B_pwr = 12);

    void set_f_osc_in(const frequency &_f_osc_in);
    
    int get_channel_divide(void);

    void enable_all(void);
    void disable_all(void);
    
    frequency get_A_frequency(void);
    frequency get_B_frequency(void);
    
    void validate(void);
    void set_osc_in(const frequency &f);
    void set_doubler_en(bool b);

    void set_sync(bool b);
    
    void dump(void);

    void tune(frequency A, frequency B);
    
  
  protected:
  };
  
};
