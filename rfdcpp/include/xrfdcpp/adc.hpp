#pragma once

#include <vector>

#include <xrfdcpp/tile.hpp>
#include <xrfdcpp/slice.hpp>

namespace rfdc {
  typedef SliceTypes<ADCTile, cfg::adc_analog, cfg::adc_digital, csr::adc> ADCSliceTypes;
  
  typedef Slice<ADCSliceTypes> ADCSlice;
  
  class ADC : public ADCSlice
  {
  public:
    typedef std::shared_ptr<ADC> ptr_t;

    ADC(types::tile_t &, int, const types::acfg_t &, const types::dcfg_t &, types::csr_t);

    virtual bool is_adc(void) { return true; }
    virtual bool is_high_speed(void);

    virtual int get_calibration_mode(void);

    virtual nyquist_zone get_nyquist_zone(void);

    dfrequency_limits get_sampling_limits(void) {
      if (is_high_speed()) {
	return dfrequency_limits(dfrequency::MHz(1000), dfrequency::MHz(4116));
      }

      return dfrequency_limits(dfrequency::MHz(500), dfrequency::MHz(2058)); 
    }
  };
  
  class ADCTile : public Tile<cfg::adc>
  {    
    volatile csr::adc_tile *csr;
    
    std::vector<ADC::ptr_t> slices;

  public:
    typedef volatile csr::adc_tile csr_t;
    
    RFDC &dc;
    const cfg::adc &conf;
    
    ADCTile(RFDC &, int, const cfg::adc &, volatile csr::adc_tile *);
    
    std::vector<ADC::ptr_t> &get_slices(void) {
      return slices;
    }
    
    ADC::ptr_t get_adc(int n) {
      return slices[n];
    }

    bool is_enabled(void);
    
    uint32_t get_path_enabled_reg(void);
  };
};  
