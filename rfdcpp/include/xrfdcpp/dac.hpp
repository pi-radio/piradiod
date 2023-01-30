#pragma once

#include <vector>

#include <xrfdcpp/xrfdcpp.hpp>

namespace rfdc {
  class DAC : public Slice<DACTile, cfg::dac_analog, cfg::dac_digital, csr::dac>, public std::enable_shared_from_this<DAC>
  {
  public:
    typedef std::shared_ptr<DAC> ptr_t;
    static constexpr bool is_adc = false;
    static constexpr int generation = 1;
    static constexpr bool high_speed = false;

    mixer::Mixer<DAC, csr::dac> mixer;
    
    DAC(DACTile *, int, const cfg::dac_analog &,
	 const cfg::dac_digital &, volatile csr::dac *);

    virtual bool is_dac(void) { return true; }

    virtual mixer::MixerBase *get_mixer(void) {
      return &mixer;
    }
    
    int get_calibration_mode(void) { return -1; }

    nyquist_zone get_nyquist_zone(void);

    dfrequency_limits get_sampling_limits(void) {
      return dfrequency_limits(dfrequency::MHz(500), dfrequency::MHz(6554)); 
    }
  };


  class DACTile : public Tile<cfg::dac, csr::dac_tile>, public std::enable_shared_from_this<DACTile>
  {
    std::vector<DAC::ptr_t> slices;
  
  public:
    typedef volatile csr::dac_tile csr_t;

    
    DACTile(const tile_params<cfg::dac, csr::dac_tile> &p);
    
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

