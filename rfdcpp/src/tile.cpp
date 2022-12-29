#include <xrfdcpp/tile.hpp>

namespace rfdc {
  Tile::Tile(volatile csr::tile *_csr) : csr(_csr)
  {
  }

  uint32_t Tile::state()
  {
    return csr->current_state;
  }

  bool Tile::cdetect_status()
  {
    return (csr->clock_detect & 1) ? true : false;
  }

  bool Tile::clock_detected()
  {
    return (csr->common_status & 1) ? true : false;
  }

  bool Tile::supplies_up()
  {
    return (csr->common_status & 2) ? true : false;
  }

  bool Tile::power_up()
  {
    return (csr->common_status & 4) ? true : false;
  }

  bool Tile::pll_locked()
  {
    return (csr->common_status & 8) ? true : false;
  }
};
