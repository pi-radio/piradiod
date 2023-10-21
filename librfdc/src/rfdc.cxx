#include <iostream>
#include <atomic>
#include <filesystem>
#include <initializer_list>
#include <vector>
#include <fmt/core.h>

extern "C" {
#include <i2c/smbus.h>
}

#include <piradio/rfdc.hpp>
#include <piradio/rfdc_dc.hpp>

namespace fs = std::filesystem;

namespace piradio
{  
  RFDC::RFDC()
  {
    int result;
    int tile, block;
    
    cfg = XRFdc_LookupConfig(0);

    if (cfg == NULL) {
      throw std::runtime_error("Unable to find config");
    }
  
    result = XRFdc_RegisterMetal(&rfdc, 0, &metal_dev);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to open rfdc metal device");
    }

    result = XRFdc_CfgInitialize(&rfdc, cfg);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to initialize rfdc");
    }

    
    result = XRFdc_GetIPStatus(&rfdc, &ip_status);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to get IP status");     
    }
    
    int n = 0;
    
    for (tile = 0; tile < 4; tile++) {
      if (!ip_status.ADCTileStatus[tile].IsEnabled ||
 	   ip_status.ADCTileStatus[tile].BlockStatusMask == 0) {
	continue;
      }

      adc_tiles[tile] = new ADCTile(*this, tile);

      //adc_tiles[tile]->reset();

      if (!adc_tiles[tile]->pll_locked()) {
	std::cerr << adc_tiles[tile]->get_id_string() << ": PLL not locked" << std::endl;
      }

      for (block = 0; block < 4; block++) {
	if (!(ip_status.ADCTileStatus[tile].BlockStatusMask & (1 << block))) {
	  continue;
	}

	adcs[n] = new ADC(*adc_tiles[tile], block);
	
	n++;
      }
    }

    n = 0;
    
    for (tile = 0; tile < 4; tile++) {
      if (!ip_status.DACTileStatus[tile].IsEnabled ||
	   ip_status.DACTileStatus[tile].BlockStatusMask == 0) {
	continue;
      }

      dac_tiles[tile] = new DACTile(*this, tile);

      //dac_tiles[tile]->reset();

      if (!dac_tiles[tile]->pll_locked()) {
	std::cerr << dac_tiles[tile]->get_id_string() << ": PLL not locked" << std::endl;
      }

      for (block = 0; block < 4; block++) {
	if (!(ip_status.DACTileStatus[tile].BlockStatusMask & (1 << block))) {
	  continue;
	}

	dacs[n] = new DAC(*dac_tiles[tile], block);
	
	n++;
      }
    }
  }

  int RFDC::reset()
  {
    return 0;
  }

  int RFDC::load_config()
  {
    int result;
    XRFdc_Config *cfg;
    cfg = XRFdc_LookupConfig(0);

    if (cfg == NULL) {
      throw std::runtime_error("Unable to find config");
    }

    XRFdc rfdc;
    struct metal_device *metal_dev;

    result = XRFdc_RegisterMetal(&rfdc, 0, &metal_dev);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to open rfdc metal device");
    }

    
    result = XRFdc_CfgInitialize(&rfdc, cfg);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to initialize rfdc");
    }

    return 0;
  }
  
};
