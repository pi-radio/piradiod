#pragma once

#include <xrfdcpp/frequency.hpp>
#include <xrfdcpp/bitfield.hpp>

namespace rfdc {
  enum class nyquist_zone {
    EVEN,
    ODD
  };

  template <class ST> class SliceBase;

  template <class Tile, class AnalogConfig, class DigitalConfig, class CSR>
  struct SliceTypes
  {
    static SliceTypes<Tile, AnalogConfig, DigitalConfig, CSR> self;
    
    typedef Tile tile_t;
    typedef AnalogConfig acfg_t;
    typedef DigitalConfig dcfg_t;
    typedef volatile CSR *csr_t;
    typedef SliceBase<decltype(self)> slice_base_t;
  };
  
  template <class ST>
  class SliceBase
  {
  public:
    typedef ST types;
    
  protected:
    types::csr_t csr;

  public:
    types::tile_t &tile;
    const int n_slice;
    const types::acfg_t &acfg;
    const types::dcfg_t &dcfg;

    SliceBase(types::tile_t &_tile,
	      int _n,
	      const types::acfg_t &_acfg,
	      const types::dcfg_t &_dcfg,
	      types::csr_t _csr) : tile(_tile),
				   n_slice(_n),
				   acfg(_acfg),
				   dcfg(_dcfg),
				   csr(_csr)
    {
    }
    
    virtual bool is_adc(void) { return false; }
    virtual bool is_dac(void) { return false; }
    virtual bool is_high_speed(void) { return false; }
    virtual int get_calibration_mode(void) { return -1; };
    virtual dfrequency_limits get_sampling_limits(void) = 0;
    virtual nyquist_zone get_nyquist_zone(void) = 0;

    frequency<double> get_sampling_rate(void) {
      return tile.sample_clock();
    }

    bool is_analog_enabled(void) {
      return bitfield(n_slice, 1).get(tile.get_analog_enabled_slices());
    }

    bool is_digital_enabled(void) {
      return bitfield(n_slice, 1).get(tile.get_digital_enabled_slices());
    }
  };
};  
