#pragma once

#include <map>

#include <piradio/xilinx-rfdc/xrfdc.h>

namespace piradio
{
  class ADC;
  class DAC;
  class ADCTile;
  class DACTile;

  namespace DCType
  {
    static const int ADC = XRFDC_ADC_TILE;
    static const int DAC = XRFDC_DAC_TILE;
  };
  
  class RFDC
  {
  public:
    XRFdc rfdc;

    RFDC();

    int n_adcs() { return adcs.size(); }
    int n_dacs() { return dacs.size(); }
    
    ADC *get_adc(int i) { return adcs.at(i); }
    DAC *get_dac(int i) { return dacs.at(i); }

    ADCTile *get_adc_tile(int i) { return adc_tiles.at(i); }
    DACTile *get_dac_tile(int i) { return dac_tiles.at(i); }

    int get_n_adc_tiles(void) { return adc_tiles.size(); }
    int get_n_dac_tiles(void) { return dac_tiles.size(); }

    int reset();

    static int load_config();
    
  private:
    XRFdc_Config *cfg;
    struct metal_device *metal_dev;

    XRFdc_IPStatus ip_status;
        
    std::map<int, ADCTile *> adc_tiles;
    std::map<int, DACTile *> dac_tiles;
    
    std::map<int, ADC *> adcs;
    std::map<int, DAC *> dacs;
  };
};
