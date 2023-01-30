#include <xrfdcpp/dac.hpp>

using namespace rfdc;

DAC::DAC(DACTile *_tile,
	 int _n,
	 const cfg::dac_analog &_acfg,
	 const cfg::dac_digital &_dcfg,
	 volatile csr::dac *_csr) : Slice(_tile, _n,
					  _acfg, _dcfg,
					  _csr),
				    mixer(*this, _csr)
{
}


nyquist_zone DAC::get_nyquist_zone(void)
{
  auto mb = tile->get_multiband_mode();

  if (mb == cfg::multiband_mode::SB ? !is_analog_enabled() : !is_digital_enabled()) {
      throw std::runtime_error("Block not available");
  }

  return csr::fields::dac::nyquist_zone.get(csr->mc_cfg0) ? nyquist_zone::EVEN : nyquist_zone::ODD;
}

DACTile::DACTile(const tile_params<cfg::dac, csr::dac_tile> &p) : Tile(p)
{
  int nslices = dc.get_n_dac_slices();
    
  slices.reserve(nslices);

  for (int i = 0; i < nslices; i++) {
    slices.emplace_back(std::make_shared<DAC>(this, i, config.analog[i], config.digital[i], &csr->dacs[i]));
  }
  
}

bool DACTile::is_enabled(void) {
  return (dc.get_tiles_enabled_mask() >> (4 + n_tile)) & 1;
}

uint32_t DACTile::get_path_enabled_reg(void) {
  return dc.get_dac_paths_enabled();
}


