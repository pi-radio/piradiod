#pragma once

#include <xrfdcpp/frequency.hpp>
#include <xrfdcpp/bitfield.hpp>

namespace rfdc {
  namespace mixer {
    class MixerBase;
  };
  
  enum class nyquist_zone {
    EVEN,
    ODD
  };

  template <typename T>
  struct type_t {
    using type = T;
  };
  
  template <typename T>
  inline constexpr type_t<T> type{};
  
  template <class Tile, class acfg_t, class dcfg_t, class CSR>
  class Slice 
  {
    friend class Mixer;
  protected:
    volatile CSR *csr;

  public:
    Tile *tile;
    const int n_slice;
    const acfg_t &acfg;
    const dcfg_t &dcfg;
    
    Slice(Tile *_tile,
	  int _n,
	  const acfg_t &_acfg,
	  const dcfg_t &_dcfg,
	  volatile CSR *_csr) : tile(_tile),
				n_slice(_n),
				acfg(_acfg),
				dcfg(_dcfg),
				csr(_csr)
    {
    }

    virtual mixer::MixerBase *get_mixer(void) = 0;
    virtual int get_calibration_mode(void) { return -1; };
    virtual dfrequency_limits get_sampling_limits(void) = 0;
    virtual nyquist_zone get_nyquist_zone(void) = 0;
    
    frequency<double> get_sampling_rate(void) {
      return tile->clock.sample_rate();
    }

    bool is_analog_enabled(void) {
      return (tile->get_analog_enabled_slices() >> n_slice) & 1;
    }

    bool is_digital_enabled(void) {
      return (tile->get_digital_enabled_slices() >> n_slice) & 1;
    }
  };
};  
