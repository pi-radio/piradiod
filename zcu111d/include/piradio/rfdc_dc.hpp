#pragma once

#include <cmath>
#include <iomanip>

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
    }

    template <class C, class F>
    int _compare_field(const C &a, const C &b, F C::*ptr, const std::string &name)
    {
      if (a.*ptr != b.*ptr) {
	std::cout << name << " differs: " << a.*ptr << " " << b.*ptr << std::endl;
	return -1;
      }

      return 0;
    }

    void display_mixer_settings(const XRFdc_Mixer_Settings &a)
    {
      std::cout << std::setw(32) << a.Freq << std::endl;
      
      std::cout << "Freq: " << a.Freq << std::endl;
      std::cout << "Phase Offset: " << a.PhaseOffset << std::endl;
      std::cout << "Event Source: " << a.EventSource << std::endl;
      std::cout << "Coarse Mix Freq: " << a.CoarseMixFreq << std::endl;
      std::cout << "Mixer Mode: " << rfdc::str::mixer_modes[a.MixerMode] << std::endl;
      std::cout << "Fine Mixer Scale: " << a.FineMixerScale << std::endl;
      std::cout << "Mixer Type: " << rfdc::str::mixer_types[a.MixerType] << std::endl;
    }
    
    
    int compare_mixer_settings(const XRFdc_Mixer_Settings &a, const XRFdc_Mixer_Settings &b)
    {
      int retval = 0;

      if (std::fabs(a.Freq - b.Freq) > 1.0) {
	std::cout << "Freq differs" << std::endl;
	retval = -1;
      }
      
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::PhaseOffset, "Phase Offset") ? -1 : retval;
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::EventSource, "Event Source") ? -1 : retval;
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::CoarseMixFreq, "Coarse Mix Freq") ? -1 : retval;
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::MixerMode, "Mixer Mode") ? -1 : retval;
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::FineMixerScale, "Fine Mixer Scale") ? -1 : retval;
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::MixerType, "Mixer Type") ? -1 : retval;

      if (retval) {
	std::cout << "A:" << std::endl;
	display_mixer_settings(a);
	std::cout << "B:" << std::endl;
	display_mixer_settings(b);
      }
      
      return retval;
    }
      
    XRFdc_Mixer_Settings get_mixer_settings(void)
    {
      int result;
      XRFdc_Mixer_Settings settings;

      result = rfdc_func(XRFdc_GetMixerSettings, &settings);

      if (result != XRFDC_SUCCESS) {
	throw std::runtime_error("Unable to get mixer settings");
      }

      return settings;
    }

    void set_mixer_settings(const XRFdc_Mixer_Settings &settings, bool verify=false)
    {
      int result;

      result = rfdc_func(XRFdc_SetMixerSettings, (XRFdc_Mixer_Settings *)&settings);

      if (result != XRFDC_SUCCESS) {
	throw std::runtime_error("Unable to set mixer settings");
      }

      if (verify) {
	assert(!compare_mixer_settings(settings, get_mixer_settings()));
      }
    }

    
  protected:
    tile_type &tile;
    int block;

    const std::string id_string;
  
    template <typename F, class... types> int rfdc_tile_func(F f, types... args)
    {
      return tile.rfdc_func(f, args...);
    }
  
    template <typename F, class... types> int rfdc_func(F f, types... args)
    {
      return tile.rfdc_func(f, block, args...);
    }

    template <typename F, class... types> int rfdc_func_no_type(F f, types... args)
    {
      return tile.rfdc_func_no_type(f, block, args...);
    }

  };


  class ADC : public RFDCBlock<ADCTile>
  {
  public:
    ADC(ADCTile &_tile, int _block);

    void set_mixer_passthrough(void);
    void tune_NCO(double freq, double phase=0.0);

    void set_attenuation(bool, float);
    
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
