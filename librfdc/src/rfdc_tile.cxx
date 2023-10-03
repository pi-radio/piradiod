#include <piradio/rfdc_tile.hpp>
#include <piradio/rfdc_str.hpp>

namespace piradio
{
  RFDCPLL::RFDCPLL(RFDCTile &_tile) : tile(_tile)
  {
  }

  XRFdc_PLL_Settings RFDCPLL::settings() const
  {
    XRFdc_PLL_Settings retval;
    
    tile.rfdc_func(XRFdc_GetPLLConfig, &retval);

    return retval;
  }

  bool RFDCPLL::enabled() const
  {
    auto s = settings();

    return s.Enabled && (s.SampleRate != 0);
  }

  
  RFDCTile::RFDCTile(RFDC &_rfdc, int _type, int _tile) : rfdc(_rfdc), type(_type),
							  tile(_tile),
							  id_string(rfdc::str::tile_types[type] + " " + std::to_string(tile)),
							  pll(*this)
  {
  }

  bool RFDCTile::enabled()
  {
    return (rfdc_func(XRFdc_CheckTileEnabled) == XRFDC_SUCCESS);
  }


  ADCTile::ADCTile(RFDC &_rfdc, int _tile) : RFDCTile(_rfdc, XRFDC_ADC_TILE, _tile)
  {    
    rfdc_func(XRFdc_SetupFIFO, 1);
  }

  DACTile::DACTile(RFDC &_rfdc, int _tile) : RFDCTile(_rfdc, XRFDC_DAC_TILE, _tile)
  {    
  }
};						  

