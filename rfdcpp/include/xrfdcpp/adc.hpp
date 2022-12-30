#pragma once

#include <vector>

#include <xrfdcpp/tile.hpp>
#include <xrfdcpp/mixer.hpp>

namespace rfdc {
  class ADC
  {
  public:
    typedef volatile csr::adc csr_t;
    typedef mixer::Mixer<ADC> mixer_t;
    
  private: 
    csr_t *csr;
    ADCTile &tile;
    
  public:
    mixer_t mixer;
    const cfg::adc_analog &acfg;
    const cfg::adc_digital &dcfg;

    
    ADC(ADCTile &, const cfg::adc_analog &, const cfg::adc_digital &, csr_t *);

    bool is_adc(void) { return true; }
    bool is_high_speed(void) { return true; } // Fix for Gen > 1

    bool is_dac(void) { return false; }
  };
  
  class ADCTile : public Tile<cfg::adc>
  {    
    volatile csr::adc_tile *csr;
    
    std::vector<ADC> slices;

  public:
    typedef volatile csr::adc_tile csr_t;
    
    RFDC &rfdc;
    const cfg::adc &conf;
    
    
    ADCTile(RFDC &, const cfg::adc &, volatile csr::adc_tile *);
    
    auto &get_slices(void) {
      return slices;
    }
    
    auto &get_adc(int n) {
      return slices[n];
    }
  };
};  
