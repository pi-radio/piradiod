#pragma once

#include <vector>

#include <xrfdcpp/tile.hpp>

namespace rfdc {
  class ADC
  {
    volatile csr::adc *csr;
    ADCTile &tile;
    
  public:
    ADC(ADCTile &, volatile csr::adc *);
  };
  
  class ADCTile : public Tile
  {
    volatile csr::adc_tile *csr;
    
    std::vector<ADC> slices;
    
  public:
    RFDC &rfdc;

    ADCTile(RFDC &, volatile csr::adc_tile *);
    
    auto &get_slices(void) {
      return slices;
    }
    
    auto &get_adc(int n) {
      return slices[n];
    }
  };
};  
