#include <iostream>

#include <piradio/rfdc_dc.hpp>
#include <piradio/rfdc_str.hpp>

namespace piradio
{
  ADC::ADC(ADCTile &_tile, int _block) : RFDCBlock(_tile, _block)
  {
  }

  void ADC::dump(void)
  {
    std::cout << "ADC " << tile.tile_no() << " " << block << std::endl;
    std::cout << "=====================" << std::endl;
    std::cout << " Mixer settings" << std::endl;
    std::cout << "  Frequency: " << mixer_settings.Freq << std::endl;
    std::cout << "  Phase: " << mixer_settings.PhaseOffset << std::endl;
    std::cout << "  Event source: " << mixer_settings.EventSource << std::endl;
    std::cout << "  Coarse Mixer Freq: " << mixer_settings.CoarseMixFreq << std::endl;
    std::cout << "  Mixer Mode: " << rfdc::str::mixer_modes[mixer_settings.MixerMode] << std::endl;
    std::cout << "  Fine Mixer Scale: " << (int)mixer_settings.FineMixerScale << std::endl;
    std::cout << "  Mixer Type: " << rfdc::str::mixer_types[mixer_settings.MixerType] << std::endl;
    std::cout << "  Data Type: " << rfdc_func(XRFdc_GetDataType) << std::endl;
    std::cout << "  PL Freq: " << rfdc_tile_func(XRFdc_GetFabClkFreq) << std::endl;
    std::cout << "  I Data: " << rfdc_func(XRFdc_GetConnectedIData) << std::endl;
    std::cout << "  Q Data: " << rfdc_func(XRFdc_GetConnectedQData) << std::endl;
  
    u32 fabric_rate;

  
    rfdc_func(XRFdc_GetFabRdVldWords, &fabric_rate);

    std::cout << "Fabric rate: " << fabric_rate << std::endl;
  }

  void ADC::set_mixer_passthrough(void)
  {
    int result;
	  
    mixer_settings.Freq = 0;
    mixer_settings.PhaseOffset = 0;
    mixer_settings.EventSource = XRFDC_EVNT_SRC_TILE;
    //mixer_settings.CoarseMixFreq = XRFDC_COARSE_MIX_BYPASS;
    mixer_settings.CoarseMixFreq = XRFDC_COARSE_MIX_SAMPLE_FREQ_BY_FOUR;
    mixer_settings.MixerMode = XRFDC_MIXER_MODE_R2C;
    mixer_settings.FineMixerScale = XRFDC_MIXER_SCALE_1P0;
    mixer_settings.MixerType = XRFDC_MIXER_TYPE_COARSE;
	  
    result = rfdc_func(XRFdc_SetMixerSettings, &mixer_settings);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Failed to update mixers settings");
    }
    
    result = tile.update_tile(XRFDC_EVENT_MIXER);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Failed to trigger tile update");
    }

    std::cout << "Data type:" << rfdc_func(XRFdc_GetDataType) << std::endl;
  }

  void ADC::tune_NCO(double freq, double phase)
  {
    XRFdc_Mixer_Settings s(mixer_settings);

    s.Freq = freq / 1e6;
    mixer_settings.PhaseOffset = phase;
    mixer_settings.EventSource = XRFDC_EVNT_SRC_TILE;
    mixer_settings.CoarseMixFreq = XRFDC_COARSE_MIX_OFF;
    mixer_settings.MixerMode = XRFDC_MIXER_MODE_R2C;
    mixer_settings.FineMixerScale = XRFDC_MIXER_SCALE_1P0;
    mixer_settings.MixerType = XRFDC_MIXER_TYPE_FINE;

    rfdc_func(XRFdc_SetMixerSettings, &s);

    tile.update_tile(XRFDC_EVENT_MIXER);

    rfdc_func(XRFdc_GetMixerSettings, &mixer_settings);

    compare_mixer_settings(&s, &mixer_settings);

    std::cout << "Data type:" << rfdc_func(XRFdc_GetDataType) << std::endl;
  }

  void ADC::set_attenuation(bool enable_ctrl, float val)
  {
    int result;
    XRFdc_DSA_Settings dsa_set;
    
    dsa_set.DisableRTS = ~enable_ctrl;
    dsa_set.Attenuation = val;

    rfdc_func_no_type(XRFdc_SetDSA, &dsa_set);
  }

};
