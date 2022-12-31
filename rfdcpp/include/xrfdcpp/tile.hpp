#pragma once

#include <stdint.h>

#include <tuple>

#include <magic_enum.hpp>

#include <xrfdcpp/config.hpp>
#include <xrfdcpp/regs.hpp>
#include <xrfdcpp/types.hpp>
#include <xrfdcpp/frequency.hpp>


namespace rfdc {
  template <class config_type> class Tile
  {
    volatile csr::tile *csr;
  public:
    const config_type &config;
    const int n_tile;
    
    Tile(volatile csr::tile *_csr,
	 int _n,
	 const config_type &_config) : csr(_csr),
				       n_tile(_n),
				       config(_config) {
    }
  
    uint32_t state() {
      return csr->current_state;
    }
    
    bool cdetect_status() {
      return (csr->clock_detect & 1) ? true : false;
    }
    
    bool clock_detected() {
      return (csr->common_status & 1) ? true : false;
    }
    
    bool supplies_up() {
      return (csr->common_status & 2) ? true : false;
    }
    
    bool power_up() {
      return (csr->common_status & 4) ? true : false;
    }
    
    bool pll_locked() {
      return (csr->common_status & 8) ? true : false;
    }

    auto sample_clock() {
      return dfrequency::GHz(config.sample_rate);
    }
    
    auto reference_clock() {
      return dfrequency::MHz(config.ref_clk_freq);
    }

    auto fabric_clock() {
      return dfrequency::MHz(config.fab_clk_freq);
    }

    auto output_clock() {
      return sample_clock() / output_div();
    }
    
    uint32_t reference_div() {
      return config.ref_clk_div;
    }
    
    uint32_t output_div() {
      return config.output_div;
    }

    cfg::multiband_mode get_multiband_mode() {
      return *magic_enum::enum_cast<cfg::multiband_mode>(config.multiband);
    }

    virtual uint32_t get_path_enabled_reg(void) = 0;

    virtual uint32_t get_digital_enabled_slices(void) {
      bitfield(16+4*n_tile,4).get(get_path_enabled_reg());
    }

    virtual uint32_t get_analog_enabled_slices(void) {
      bitfield(16+4*n_tile,4).get(get_path_enabled_reg());
    }
  };
};
