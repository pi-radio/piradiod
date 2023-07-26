#include <iostream>
#include <map>

#include <piradio/xilinx-zcu111/xrfdc.h>
#include <piradio/rfdc_str.hpp>

namespace piradio
{
  namespace rfdc
  {
    namespace str
    {
      const cstrmap mixer_modes = {
	{ XRFDC_MIXER_MODE_OFF, "off" },
	{ XRFDC_MIXER_MODE_C2C, "C2C" },
	{ XRFDC_MIXER_MODE_C2R, "C2R" },
	{ XRFDC_MIXER_MODE_R2C, "R2C" },
	{ XRFDC_MIXER_MODE_R2R, "R2R" }
      };
      
      const cstrmap mixer_types = {
	{ XRFDC_MIXER_TYPE_OFF, "off" },
      { XRFDC_MIXER_TYPE_COARSE, "coarse" },
      { XRFDC_MIXER_TYPE_FINE, "fine" },
      { XRFDC_MIXER_TYPE_DISABLED, "disabled" },
      };
      
      const cstrmap tile_types = {
	{ XRFDC_ADC_TILE, "ADC" },
	{ XRFDC_DAC_TILE, "DAC" }
      };
    };
  }; 
};
