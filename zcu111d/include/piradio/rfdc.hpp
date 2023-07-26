#pragma once

#include <map>

#include <piradio/xilinx-zcu111/xrfdc.h>

namespace piradio
{
  class ADC;
  class DAC;
  class ADCTile;
  class DACTile;
  
  class RFDC
  {
  public:
    XRFdc rfdc;

    RFDC();

    ADC *get_adc(int i) { return adcs.at(i); }
    DAC *get_dac(int i) { return dacs.at(i); }

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
}
