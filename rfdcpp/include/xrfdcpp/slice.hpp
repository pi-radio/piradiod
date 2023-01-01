#pragma once

#include <xrfdcpp/slice_base.hpp>
#include <xrfdcpp/mixer.hpp>

namespace rfdc {
  template <class ST>
  class Slice : public SliceBase<ST>
  {
  public:
    mixer::Mixer<ST> mixer;

    Slice(ST::tile_t &_tile,
	  int _n,
	  const ST::acfg_t &_acfg,
	  const ST::dcfg_t &_dcfg,
	  ST::csr_t _csr) : SliceBase<ST>(_tile, _n, _acfg, _dcfg, _csr),
			    mixer(*this, _csr)
    {
    }
  };
};
