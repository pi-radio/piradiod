#pragma once

#include <vector>

#include <xrfdcpp/xrfdcpp.hpp>

namespace rfdc {
  class DAC
  {
    volatile csr::dac *csr;
    DACTile &tile;
    
  public:
    DAC(DACTile &, volatile csr::dac *);
  };


  class DACTile : public Tile
  {
    volatile csr::dac_tile *csr;

    std::vector<DAC> slices;
  
  public:
    RFDC &rfdc;

    DACTile(RFDC &, volatile csr::dac_tile *);

    auto &get_slices(void) {
      return slices;
    }

    auto &get_dac(int n) {
      return slices[n];
    }  
  };
};
