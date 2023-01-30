#include <xrfdcpp/xrfdcpp.hpp>
#include <xrfdcpp/mixer.hpp>
#include <xrfdcpp/config.hpp>

namespace rfdc{
  nyquist_zone LSADC::get_nyquist_zone(void)
  {
    return _get_nyquist_zone();
  }

  int HSADC::get_calibration_mode(void) {
    auto mode = csr::fields::adc::calibration_mode.get(csr->ti_dcb_crl0);
    
    if (mode == 0) {
      return 2;
    } else {
      return 1;
    }

    throw std::runtime_error("Unhandled calibration mode");
  }

  nyquist_zone ADC::_get_nyquist_zone(void)
  {
    auto mb = tile->get_multiband_mode();

    if (mb == cfg::multiband_mode::SB ? !is_analog_enabled() : !is_digital_enabled()) {
      throw std::runtime_error("Block not available");
    }
  
    // The Xilinx code has this disaster:
    //
    // if ((XRFdc_IsHighSpeedADC(InstancePtr, Tile_Id) == 1) && (Block_Id == XRFDC_BLK_ID1) &&
    //     (Type == XRFDC_ADC_TILE)) {
    //   Block_Id = XRFDC_BLK_ID2;
    // }
    //

    auto retval = csr::fields::adc::nyquist_zone.get(csr->ti_tisk_crl0) ? nyquist_zone::EVEN : nyquist_zone::ODD;


    return retval;
  }

  nyquist_zone HSADC::get_nyquist_zone(void)
  {
    auto zone = _get_nyquist_zone();

    if (get_calibration_mode() == 1) {
      zone = (zone == nyquist_zone::ODD) ? nyquist_zone::EVEN : nyquist_zone::ODD;
    }

    return zone;
  }

  ADCTile::ADCTile(const tile_params<cfg::adc, csr::adc_tile> &p) : Tile(p)
  {
    int nslices = dc.get_n_adc_slices();

    if (nslices == 2) {
      for (int i = 0; i < nslices; i++) {
	// High speed ADCs use 1 and 3
	int ci = (2 * i + 1);
      
	slices.emplace_back(std::make_shared<HSADC>(this, ci, config.analog[ci], config.digital[ci], &csr->adcs[2 * i], &csr->adcs[ci])); 
      }
    } else {
      for (int i = 0; i < nslices; i++) {
	slices.emplace_back(std::make_shared<LSADC>(this, i, config.analog[i], config.digital[i], &csr->adcs[i])); 
      }
    }
  }

  bool ADCTile::is_enabled(void) {
    return (dc.get_tiles_enabled_mask() >> n_tile) & 1;
  }

  uint32_t ADCTile::get_path_enabled_reg(void) {
    return dc.get_adc_paths_enabled();
  }
}
