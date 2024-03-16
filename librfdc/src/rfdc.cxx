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

  int RFDC::load_config()
  {
  }

  void RFDC::startup()
  {
    XRFdc_StartUp(&rfdc, 0, -1);
    XRFdc_StartUp(&rfdc, 1, -1);
  }
  
  void RFDC::shutdown()
  {
    XRFdc_Shutdown(&rfdc, 0, -1);
    XRFdc_Shutdown(&rfdc, 1, -1);
  }

  void RFDC::reset()
  {
    XRFdc *p = &rfdc;
    using std::memory_order_seq_cst;
    XRFdc_WriteReg16(p, 0, 4, 1);
  }
  
  void RFDC::restart()
  {
    XRFdc_Reset(&rfdc, 0, -1);
    XRFdc_Reset(&rfdc, 1, -1);    
  }

  bool check_status();

  XRFdc_IPStatus RFDC::get_status()
  {
    int result = XRFdc_GetIPStatus(&rfdc, &ip_status);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to get IP status");     
    }

    return ip_status;
  }  

  void RFDC::MTSSync()
  {
    int i;
    
    XRFdc_MultiConverter_Sync_Config config;
    
    /* Initialize DAC MTS Settings */
    XRFdc_MultiConverter_Init (&config, 0, 0, XRFDC_TILE_ID0);
    config.Tiles = 0x3;	/* Sync DAC tiles 0 and 1 */
    
    auto status = XRFdc_MultiConverter_Sync(&rfdc, XRFDC_DAC_TILE, &config);
    
    if(status == XRFDC_MTS_OK){
      std::cout << "INFO : DAC Multi-Tile-Sync completed successfully" << std::endl;
    } else {
      std:: cout << "ERROR : DAC Multi-Tile-Sync did not complete successfully. Error code is "
		 << status << std::endl;
    }

    for(i=0; i<2; i++) {
      std::cout << "DAC" << i << ": Latency: "
		<< config.Latency[i] << " Offset: "
		<< config.Offset[i] << std::endl;
    }

    
    XRFdc_MultiConverter_Init (&config, 0, 0, XRFDC_TILE_ID0);

    config.Tiles = 0xF;
    
    status = XRFdc_MultiConverter_Sync(&rfdc, XRFDC_ADC_TILE, &config);
    
    if(status == XRFDC_MTS_OK){
      std::cout << "INFO : ADC Multi-Tile-Sync completed successfully" << std::endl;
    } else {
      std:: cout << "ERROR : ADC Multi-Tile-Sync did not complete successfully. Error code is "
		 << status << std::endl;
    }
    
    for(i=0; i<2; i++) {
      std::cout << "DAC" << i << ": Latency: "
		<< config.Latency[i] << " Offset: "
		<< config.Offset[i] << std::endl;
    }
  }
};
