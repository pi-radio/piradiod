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
      return status;
    }

    for(i=0; i<2; i++) {
      std::cout << "DAC" << i << ": Latency: "
		<< config.Latency[i] << " Offset: "
		<< config.Offset[i] << std::endl;
    }

    
    XRFdc_MultiConverter_Init (&config, 0, 0, XRFDC_TILE_ID0);

    config.Tiles = 0xF;
    
    auto status = XRFdc_MultiConverter_Sync(&rfdc, XRFDC_ADC_TILE, &config);
    
    if(status == XRFDC_MTS_OK){
      std::cout << "INFO : ADC Multi-Tile-Sync completed successfully" << std::endl;
    } else {
      std:: cout << "ERROR : ADC Multi-Tile-Sync did not complete successfully. Error code is "
		 << status << std::endl;
      return status;
    }
    
    for(i=0; i<2; i++) {
      std::cout << "DAC" << i << ": Latency: "
		<< config.Latency[i] << " Offset: "
		<< config.Offset[i] << std::endl;
    }

    return XRFDC_MTS_OK;
  }
};
