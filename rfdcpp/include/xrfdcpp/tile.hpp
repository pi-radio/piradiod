#include <stdint.h>

#include <tuple>

#pragma once

#include <xrfdcpp/config.hpp>
#include <xrfdcpp/regs.hpp>
#include <xrfdcpp/types.hpp>

namespace rfdc {
  template <class config_type> class Tile
  {
    volatile csr::tile *csr;
  public:
    const config_type &config;
    
    Tile(volatile csr::tile *_csr, const config_type &_config) : csr(_csr), config(_config) {
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

    double sample_clock() {
      return config.sample_rate * 1.0e9;
    }
    
    double reference_clock() {
      return config.ref_clk_freq * 1.0e6;
    }

    double fabric_clock() {
      return config.fab_clk_freq * 1.0e6;
    }

    double output_clock() {
      return sample_clock() / output_div();
    }
    
    uint32_t reference_div() {
      return config.ref_clk_div;
    }
    
    uint32_t output_div() {
      return config.output_div;
    }

  };
};
