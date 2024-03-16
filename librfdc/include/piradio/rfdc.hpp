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

    void startup();
    void shutdown();

    void reset();
    
    void restart();

    bool check_status();

    void MTSSync();

    XRFdc_IPStatus get_status();
    
    int load_config();
    
    inline u64 read64(u32 addr) { using namespace std; return metal_io_read64(rfdc.io, addr); }
    inline u32 read32(u32 addr) { using namespace std; return metal_io_read32(rfdc.io, addr); }
    inline u16 read16(u32 addr) { using namespace std; return metal_io_read16(rfdc.io, addr); }
    inline u8 read8(u32 addr) { using namespace std; return metal_io_read8(rfdc.io, addr); }

    inline void write64(u32 addr, u64 v) { using namespace std; metal_io_write64(rfdc.io, addr, v); }
    inline void write32(u32 addr, u32 v) { using namespace std; metal_io_write32(rfdc.io, addr, v); }
    inline void write16(u32 addr, u16 v) { using namespace std; metal_io_write16(rfdc.io, addr, v); }
    inline void write8(u32 addr, u8 v) { using namespace std; metal_io_write8(rfdc.io, addr, v); }

    inline u32 dac_enabled_mask() { return read32(XRFDC_DAC_PATHS_ENABLED_OFFSET); }
    inline u32 adc_enabled_mask() { return read32(XRFDC_ADC_PATHS_ENABLED_OFFSET); }
    
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
