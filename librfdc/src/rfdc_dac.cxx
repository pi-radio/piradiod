#include <iostream>

#include <piradio/rfdc_dc.hpp>
#include <piradio/rfdc_str.hpp>

namespace piradio
{
  DAC::DAC(DACTile &_tile, int _block) : RFDCBlock(_tile, _block)
  {
  }
};
