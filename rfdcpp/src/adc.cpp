#include <xrfdcpp/xrfdcpp.hpp>
#include <xrfdcpp/mixer.hpp>
#include <xrfdcpp/config.hpp>


using namespace rfdc;

ADC::ADC(ADCTile &_tile,
	 const cfg::adc_analog &_acfg,
	 const cfg::adc_digital &_dcfg,
	 volatile csr::adc *_csr) : tile(_tile),
				    acfg(_acfg), dcfg(_dcfg),
				    mixer(*this, _csr),
				    csr(_csr)
{
}


ADCTile::ADCTile(RFDC &_rfdc,
		 const cfg::adc &_conf,
		 volatile csr::adc_tile *_csr) : Tile(&_csr->t),
						 conf(_conf),
						 csr(_csr),
						 rfdc(_rfdc)
{
  for (int i = 0; i < rfdc.get_n_adc_slices(); i++) {
    slices.emplace_back(*this, conf.analog[i], conf.digital[i], &csr->adcs[i]);
  }
}

