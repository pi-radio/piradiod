#include <xrfdcpp/xrfdcpp.hpp>
#include <xrfdcpp/mixer.hpp>


using namespace rfdc;

ADC::ADC(ADCTile &_tile, volatile csr::adc *_csr) : tile(_tile), csr(_csr)
{
}


ADCTile::ADCTile(RFDC &_rfdc, volatile csr::adc_tile *_csr) : Tile(&_csr->t), csr(_csr), rfdc(_rfdc)
{
  for (int i = 0; i < rfdc.get_n_adc_slices(); i++) {
    slices.emplace_back(*this, &csr->adcs[i]);
  }
}

