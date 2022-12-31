#pragma once

#include <vector>

#include <xrfdcpp/xrfdcpp.hpp>

namespace rfdc {
  typedef SliceTypes<DACTile, cfg::dac_analog, cfg::dac_digital, csr::dac> DACSliceTypes;
  
  typedef Slice<DACSliceTypes> DACSlice;

  class DAC : public DACSlice
  {
  public:
    typedef std::shared_ptr<DAC> ptr_t;
    
    DAC(DACTile &, int, const cfg::dac_analog &,
	 const cfg::dac_digital &, volatile csr::dac *);

    virtual bool is_dac(void) { return true; }

    frequency<double> get_sampling_rate(void);

    int get_calibration_mode(void) { return -1; }

    nyquist_zone get_nyquist_zone(void);

    dfrequency_limits get_sampling_limits(void) {
      return dfrequency_limits(dfrequency::MHz(500), dfrequency::MHz(6554)); 
    }
  };


  class DACTile : public Tile<cfg::dac>
  {
    volatile csr::dac_tile *csr;

    std::vector<DAC::ptr_t> slices;
  
  public:
    typedef volatile csr::dac_tile csr_t;

    RFDC &dc;
    const cfg::dac &conf;
    
    DACTile(RFDC &, int, const cfg::dac &, volatile csr::dac_tile *);

    std::vector<DAC::ptr_t> &get_slices(void) {
      return slices;
    }

    DAC::ptr_t get_dac(int n) {
      return slices[n];
    }

    bool is_enabled(void);

    virtual uint32_t get_path_enabled_reg(void);
  };
};

