#include <xrfdcpp/dac.hpp>

using namespace rfdc;

DAC::DAC(DACTile &_tile, volatile csr::dac *_csr) : tile(_tile), csr(_csr)
{
}

DACTile::DACTile(RFDC &_rfdc, const cfg::dac &_conf, volatile csr::dac_tile *_csr) : Tile(&_csr->t, _conf), csr(_csr), rfdc(_rfdc)
{
  for (int i = 0; i < rfdc.get_n_dac_slices(); i++) {
    slices.emplace_back(*this, &csr->dacs[i]);
  }
  
}

