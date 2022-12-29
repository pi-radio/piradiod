#include <stdint.h>

#include <tuple>

#pragma once

#include <xrfdcpp/config.hpp>
#include <xrfdcpp/regs.hpp>
#include <xrfdcpp/types.hpp>

namespace rfdc {
  class Tile
  {
    volatile csr::tile *csr;
  public:
    Tile(volatile csr::tile *);
  
    uint32_t state();
    
    bool cdetect_status();
    
    bool clock_detected();
    bool supplies_up();
    bool power_up();
    bool pll_locked();  
  };
};
