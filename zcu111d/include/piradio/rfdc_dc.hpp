#pragma once

#include <piradio/xilinx-zcu111/xrfdc.h>
#include <piradio/rfdc_tile.hpp>
#include <piradio/rfdc_str.hpp>

namespace piradio
{

  template <class tile_type>
  class RFDCBlock
  {
  public:
    RFDCBlock(tile_type &_tile, int _block) : tile(_tile),
					      block(_block),
					      id_string(_tile.get_id_string() + " " + std::to_string(block))
    {
      int result;

      std::cout << "Get MIxer settings" << std::endl;
      
      result = rfdc_func(XRFdc_GetMixerSettings, &mixer_settings);

      if (result != XRFDC_SUCCESS) {
	std::cerr << id_string << ": Unable to read mixer settings " << std::endl;
      }

      std::cout << "Done" << std::endl;
    }

    int compare_mixer_settings(XRFdc_Mixer_Settings *a, XRFdc_Mixer_Settings *b)
    {
      if (memcmp(a, b, sizeof(*a)) == 0) return 0;

      std::cout << "Freq: " << a->Freq << " " << b->Freq << std::endl;
      std::cout << "Phase Offset: " << a->PhaseOffset << " " << b->PhaseOffset << std::endl;
      std::cout << "Event Source: " << a->EventSource << " " << b->EventSource << std::endl;
      std::cout << "Coarse Mix Freq: " << a->CoarseMixFreq << " " << b->CoarseMixFreq << std::endl;
      std::cout << "Mixer Mode: " << rfdc::str::mixer_modes[a->MixerMode] << " " << rfdc::str::mixer_modes[b->MixerMode] << std::endl;
      std::cout << "Fine Mixer Scale: " << a->FineMixerScale << " " << b->FineMixerScale << std::endl;
      std::cout << "Mixer Type: " << rfdc::str::mixer_types[a->MixerType] << " " << rfdc::str::mixer_types[b->MixerType] << std::endl;

      return -1;
    }
    
    
  protected:
    tile_type &tile;
    int block;

    const std::string id_string;
  
    XRFdc_Mixer_Settings mixer_settings;

  
    template <typename F, class... types> int rfdc_tile_func(F f, types... args)
    {
      return tile.rfdc_func(f, args...);
    }
  
    template <typename F, class... types> int rfdc_func(F f, types... args)
    {
      return tile.rfdc_func(f, block, args...);
    }
  };


  class ADC : public RFDCBlock<ADCTile>
  {
  public:
    ADC(ADCTile &_tile, int _block);

    void set_mixer_passthrough(void);
    void tune_NCO(double freq, double phase=0.0);

    void dump(void);
    
  private:
  
  
  };

  class DAC : public RFDCBlock<DACTile>
  {
  public:
    DAC(DACTile &_tile, int _block);
  
  private:
  
  };

};
