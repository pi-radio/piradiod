#include <xrfdcpp/xrfdcpp.hpp>
#include <xrfdcpp/mixer.hpp>
#include <xrfdcpp/config.hpp>


using namespace rfdc;

ADC::ADC(types::tile_t &_tile, int _n,
    const types::acfg_t &_acfg,
    const types::dcfg_t &_dcfg,
    types::csr_t _csr) : ADCSlice(_tile, _n,
				  _acfg, _dcfg,
				  _csr)
{
}

bool ADC::is_high_speed(void)
{
  int n = tile.dc.get_n_adc_slices();
  
  return n == 2;
}

int ADC::get_calibration_mode(void) {
  if(tile.dc.get_generation() < 3) {
    auto mode = bitfield(11, 4).get(csr->ti_dcb_crl0);
    
    if (mode == 0) {
      return 2;
    } else {
      return 1;
    }
  } else {
    // TODO
  }

  throw std::runtime_error("Unhandled calibration mode");
}

nyquist_zone ADC::get_nyquist_zone(void)
{
  auto mb = tile.get_multiband_mode();
}

ADCTile::ADCTile(RFDC &_dc,
		 int _n,
		 const cfg::adc &_conf,
		 volatile csr::adc_tile *_csr) : Tile(&_csr->t, _n, _conf),
						 conf(_conf),
						 csr(_csr),
						 dc(_dc)
{
  int nslices = dc.get_n_adc_slices();

  slices.reserve(nslices);

  for (int i = 0; i < nslices; i++) {
    // High speed ADCs use 1 and 3
    int ci = (nslices == 2) ? (2 * i + 1) : i;
    
    slices.emplace_back(new ADC(*this, ci, conf.analog[ci], conf.digital[ci], &csr->adcs[ci]));
  }
}

bool ADCTile::is_enabled(void) {
  return bitfield(n_tile, 1).get(dc.get_tiles_enabled_mask());
}

uint32_t ADCTile::get_path_enabled_reg(void) {
  return dc.get_adc_paths_enabled();
}
