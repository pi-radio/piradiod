#include <vector>
#include <cmath>
#include <stdexcept>
#include <map>
#include <iostream>
#include <cmath>
#include <cassert>
#include <iomanip>
#include <numeric>
#include <algorithm>

#include <piradio/lmx2594.hpp>

namespace piradio
{
  std::array plldiv{
    2, 4, 6, 8, 12, 16, 24, 32, 72, 96, 128, 192, 256, 384, 512, 768
  };
  
  class InternalVCO
  {
    int sel;
    frequency_range fr;
    nrange gain;
    nrange amp_cal;
    nrange cap_ctrl;
  
  public:
    InternalVCO(int _sel,
		const frequency_range &_fr,
		const nrange &_gain,
		const nrange &_amp_cal,
		const nrange &_cap_ctrl) : sel(_sel),
					   fr(_fr),
					   gain(_gain),
					   amp_cal(_amp_cal),
					   cap_ctrl(_cap_ctrl)
    {      
    }



    bool in_range(const frequency &f) { return fr.in_co(f); }
    int get_sel() { return sel; }
    int get_gain(const frequency &f) { return gain.lerp(fr.bc(f)); }
    int get_amp_cal(const frequency &f) { return cap_ctrl.lerp(fr.bc(f)); }
    int get_cap_ctrl(const frequency &f) { return gain.lerp(fr.bc(f)); }
  };

  std::vector<InternalVCO> LMX2594_VCO{
    { 1, { MHz(7500), MHz(8600) }, {73, 114 },  { 299, 240 }, { 164, 12 } },
    { 2, { MHz(8600), MHz(9800) }, { 61, 121 }, { 356, 247 }, { 165, 16 } },
    { 3, { MHz(9800), MHz(10800) }, { 98, 132 }, { 324, 224 }, { 158, 19 } },
    { 4, { MHz(10800), MHz(12000) }, { 106, 141 },  { 383, 244 }, { 140, 0} },
    // Frequency Hole
    { 4, { MHz(11900), MHz(12100) }, { -1, -1 },  { 100, 100 }, { 0, 0 } },
    { 5, { MHz(12000), MHz(12900) }, { 170, 215 },  { 205, 146 }, { 183, 36 } },
    { 6, { MHz(12900), MHz(13900) }, { 172, 218 }, { 242, 163 }, { 155, 6 } },
    { 7, { MHz(13900), MHz(15000) }, { 182, 239 }, { 323, 244 }, { 175, 19 } }
  };

  LMX2594::LMX2594(const frequency &_f_osc_in, uint8_t A_pwr, uint8_t B_pwr) :
    osc_in([this](void) { return f_osc_in; }),
    osc_2x(osc_in),
    osc_pre_div(osc_2x),
    osc_mult(osc_pre_div),
    osc_post_div(osc_mult),
    VCO(osc_post_div),
    channel_divider(VCO)
  {
    osc_2x.compute = [this](frequency f) { return config.osc_2x ? 2*f : f; };
    
    osc_pre_div.compute = [this](frequency f) { return f / config.pll_r_pre; };
    
    osc_mult.compute = [this](frequency f) { return f * config.mult; };
    
    osc_post_div.compute = [this](frequency f) { return f / config.pll_r; };

    VCO.compute = [this](frequency f) { return f * (config.pll_n + (double)config.pll_num/config.pll_den);  };
    
    channel_divider.compute = [this](frequency f) { return f / get_channel_divide();  };

    set_f_osc_in(_f_osc_in);

    assert(A_pwr < 64);
    assert(B_pwr < 64);
    
    config.outa_pwr = A_pwr;
    config.outb_pwr = B_pwr;

    config.muxout_ld_sel = 1;
    config.cpg = 7;
    config.mash_order = 3;
    config.mash_reset_n = 1;
    config.inpin_ignore = 1;
    config.ld_type = 1;

    // Straight up copying cra
    config.sysref_en = 0;
    config.sysref_div = 1;
    config.sysref_div_pre = 4;
    
    config.jesd_dac1_ctrl = 0x3F;
    config.ramp_thresh = 26214;
    config.ramp_triga = 1;
    config.ramp_trigb = 1;
    config.ramp0_next = 1;    
    config.ramp0_next_trig = 1;
    config.ramp1_next_trig = 1;
    config.ramp_manual = 1;
    config.out_force = 1;
  }

  void LMX2594::set_f_osc_in(const frequency &_f_osc_in)
  {
    f_osc_in = _f_osc_in;

    /*
      The low noise doubler can be used to increase the
      phase detector frequency to improve phase noise and
      avoid spurs. This is in reference to the OSC_2X bit.     
    */    
    config.osc_2x = 0;

    /*
      Only use the Pre-R divider if the multiplier is used and
      the input frequency is too high for the multiplier.
     */
    config.pll_r_pre = 1;
    config.mult = 1;
    config.pll_r = 1;

    if (osc_post_div.output_frequency() < MHz(2.5)) {
      config.fcal_lpfd_adj = 3;
    } else if(osc_post_div.output_frequency() < MHz(5)) {
      config.fcal_lpfd_adj = 2;
    } else if(osc_post_div.output_frequency() < MHz(10)) {
      config.fcal_lpfd_adj = 1;
    } else {
      config.fcal_lpfd_adj = 0;
    } 
    
    if (osc_post_div.output_frequency() > MHz(200)) {
      config.fcal_hpfd_adj = 3;
    } else if(osc_post_div.output_frequency() > MHz(150)) {
      config.fcal_hpfd_adj = 2;
    } else if(osc_post_div.output_frequency() > MHz(100)) {
      config.fcal_hpfd_adj = 1;
    } else {
      config.fcal_hpfd_adj = 0;
    } 

    config.acal_cmp_dly = f_osc_in.MHz() / (10*std::pow(2.0, config.cal_clk_div));

    config.acal_cmp_dly = std::max(config.acal_cmp_dly, (uint16_t)10);
    config.acal_cmp_dly = std::min(config.acal_cmp_dly, (uint16_t)25);      
  }

  std::tuple<uint32_t, uint32_t>  to_frac(double d)
  {
    uint32_t precision = 2147833380;

    uint32_t num = std::round(d * precision);

    uint32_t v = std::gcd(num, precision);

    return std::make_tuple(num / v, precision / v);
  }

  void LMX2594::enable_all(void)
  {
    config.outa_pd = 0;
    config.outb_pd = 0;
  }
  
  void LMX2594::disable_all(void)
  {
    config.outa_pd = 1;
    config.outb_pd = 1;
  }
  
  void LMX2594::tune(frequency A, frequency B)
  {
    LMX2594Config new_config(config);

    frequency VCOfreq;
    
    if (A >= MHz(15000.0)) {
	throw std::runtime_error("A frequency too high");
    }
    
    if (A >= MHz(7500.0)) {
      // We need to use the VCO directly
      if (B > A) throw std::runtime_error("B frequency can not be larger than A when using the VCO directly");

      VCOfreq = A;
      new_config.outa_mux = mux_select::VCO;
    } else {
      int i;

      new_config.chdiv = plldiv.size();

      for (i = 0; i < plldiv.size(); i++) {
	auto am = A * plldiv[i];
	
	if (am >= MHz(7500.0) && am <= MHz(15000.0)) {
	  new_config.chdiv = i;
	}
      }

      if (new_config.chdiv == plldiv.size()) {
	throw std::runtime_error("A frequency too low");
      }

      VCOfreq = A * plldiv[new_config.chdiv];
      new_config.outa_mux = mux_select::CHANNEL_DIVIDER;
    }

    if (B == VCOfreq) {
      new_config.outb_mux = mux_select::VCO;
    } else if (new_config.outa_mux == 1) {
      if (A != B) {
	throw std::runtime_error("B frequency must be equal to A when using the channel divider");
      }
      new_config.outb_mux = mux_select::CHANNEL_DIVIDER;
    } else {
      int div = VCOfreq / B;

      auto i = std::find(plldiv.begin(), plldiv.end(), div);
      
      if (i == std::end(plldiv)) {
	throw std::runtime_error("B divisor is not valid");
      }

      new_config.chdiv = i - plldiv.begin();
    }


    if (new_config.chdiv != 0 &&
	new_config.outa_mux != mux_select::VCO &&
	new_config.outb_mux != mux_select::VCO) {
      new_config.seg1_en = 1;
    }
    
    double d = VCOfreq / osc_post_div.output_frequency();

    uint64_t ivco_freq = (uint64_t)VCOfreq.Hz();
    uint64_t iout_freq = (uint64_t)osc_post_div.output_frequency().Hz();

    uint64_t rem = ivco_freq % iout_freq;
    
    
    new_config.pll_n = ivco_freq/iout_freq;

    uint64_t gcd = std::gcd(rem, iout_freq);
    
    new_config.pll_num = rem / gcd;
    new_config.pll_den = iout_freq / gcd;
    
    ///std::tie(new_config.pll_num, new_config.pll_den) = to_frac(d - (int)d);

    for (auto vcoc : LMX2594_VCO) {
      if (vcoc.in_range(VCOfreq)) {
	new_config.vco_sel = vcoc.get_sel();
	new_config.vco_daciset = vcoc.get_amp_cal(VCOfreq);
	new_config.vco_daciset_strt = vcoc.get_amp_cal(VCOfreq);
	new_config.vco_capctrl = vcoc.get_cap_ctrl(VCOfreq);
	new_config.vco_capctrl_strt = vcoc.get_cap_ctrl(VCOfreq);
	break;
      }
    }

    frequency max_fpd;
    uint32_t min_n;
    
    if (config.mash_order == 0) {
      max_fpd = MHz(400);
      
      if (VCOfreq <= MHz(12500)) {
	min_n = 28;
	new_config.pfd_dly_sel = 1;
      } else {
	min_n = 32;
	new_config.pfd_dly_sel = 2;
      }
    } else if (config.mash_order < 4) {
      max_fpd = MHz(300);

      if (config.mash_order == 1) {
	if (VCOfreq <= MHz(10000)) {
	  min_n = 28;
	  new_config.pfd_dly_sel = 1;
	} else if (VCOfreq <= MHz(12500)) {
	  min_n = 32;
	  new_config.pfd_dly_sel = 2;
	} else {
	  min_n = 36;
	  new_config.pfd_dly_sel = 3;
	}
      } else if (config.mash_order == 2) {
	if (VCOfreq <= MHz(10000)) {
	  min_n = 32;
	  new_config.pfd_dly_sel = 2;
	} else {
	  min_n = 36;
	  new_config.pfd_dly_sel = 3;
	}
      } else if (config.mash_order == 3) {
	if (VCOfreq <= MHz(10000)) {
	  min_n = 36;
	  new_config.pfd_dly_sel = 3;
	} else {
	  min_n = 40;
	  new_config.pfd_dly_sel = 4;
	}
      }
      
    } else if (config.mash_order == 4) {
      max_fpd = MHz(240);

      if (VCOfreq <= MHz(10000)) {
	min_n = 44;
	new_config.pfd_dly_sel = 4;
      } else {
	min_n = 48;
	new_config.pfd_dly_sel = 5;
      }
    } else {
      throw std::runtime_error("Invalid MASH order");
    }

    if (osc_post_div.output_frequency() > max_fpd) {
      throw std::runtime_error("Phase detector frequency exceeded for MASH order");
    }

    if (new_config.pll_n < min_n) {
      throw std::runtime_error("PLL divider lower than minimum");      
    }


    new_config.fcal_en = 1;
    
    new_config.acal_cmp_dly = 10;
    new_config.vco_capctrl = 183;
    new_config.vco_sel = 4;
    new_config.vco_daciset = 128;
    new_config.vco_daciset_strt = 300;
    new_config.vco_capctrl_strt = 1;
    new_config.mash_rst_count = 0xc350;

    new_config.ramp_thresh = 0x266666;
    new_config.ramp_limit_high = 0x1E000000;    
    new_config.ramp_limit_low = 0x1d3000000;
    new_config.ramp0_inc = 0x2000000;
    new_config.ramp1_inc = 0x3F800000;
    
    config = new_config;
  }

  frequency LMX2594::get_A_frequency(void)
  {
    switch(config.outa_mux) {
    case 0:
      return channel_divider.output_frequency();
    case 1:
      return VCO.output_frequency();
    case 3:
      return Hz(0);
    }

    throw std::runtime_error("Invalid OUTA mux");
  }

  frequency LMX2594::get_B_frequency(void)
  {
    switch(config.outb_mux) {
    case 0:
      return channel_divider.output_frequency();
    case 1:
      return VCO.output_frequency();
    case 2:
      return sysref_freq;
    case 3:
      return Hz(0);      
    }

    throw std::runtime_error("Invalid OUTA mux");
  }

  
  int LMX2594::get_channel_divide(void)
  {
    if (config.chdiv >= plldiv.size())
      throw std::runtime_error("Invalid channel divider");

    return plldiv[config.chdiv];
  }
  
  void LMX2594::validate(void)
  {
    if (f_osc_in.MHz() < 5.0) throw std::runtime_error("Minimum frequency for OSC_IN is 5.0MHz");
    if (f_osc_in.MHz() > 1400.0) throw std::runtime_error("Maximum frequency for OSC_IN is 1400.0MHz");

    if (osc_2x.output_frequency().MHz() > 1400.0) throw std::runtime_error("Maximum frequency for OSC_IN doubler is 1400.0MHz");

    if (config.mult == 2) throw std::runtime_error("Pre-mult of 2 not supported");
    
  }
  
  void LMX2594::set_osc_in(const frequency &f)
  {
    f_osc_in = f;
    validate();
  }

  void LMX2594::set_doubler_en(bool b)
  {
    config.osc_2x = b;
  }
  

  void LMX2594::dump(void)
  {
    std::cout << "Input frequency: " << f_osc_in << std::endl;
    std::cout << " OSC2X output: " << osc_2x.output_frequency() << std::endl;
    std::cout << " OSC pre-divider output: " << osc_pre_div.output_frequency() << std::endl;
    std::cout << " OSC multiplier output: " << osc_mult.output_frequency() << std::endl;
    std::cout << " OSC post-divier output: " << osc_post_div.output_frequency() << std::endl;
    std::cout << " VCO output: " << VCO.output_frequency() << std::endl;
    std::cout << " VCO N: " << config.pll_n << "+" << config.pll_num << "/" << config.pll_den << std::endl;
    std::cout << " Channel divider output: " << channel_divider.output_frequency() << std::endl;
    std::cout << std::endl;
    std::cout << " A freqeuency: " << get_A_frequency() << std::endl;
    std::cout << " A power: " << config.outa_pwr << std::endl;
    
    std::cout << std::endl;
    std::cout << " B freqeuency: " << get_B_frequency() << std::endl;
    std::cout << " B power: " << config.outb_pwr << std::endl;
  }
};
