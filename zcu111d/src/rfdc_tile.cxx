#include <piradio/rfdc_tile.hpp>
#include <piradio/rfdc_str.hpp>

namespace piradio
{
  RFDCTile::RFDCTile(RFDC &_rfdc, int _type, int _tile) : rfdc(_rfdc), type(_type),
							  tile(_tile),
							  id_string(rfdc::str::tile_types[type] + " " + std::to_string(tile))
  {
  }

  ADCTile::ADCTile(RFDC &_rfdc, int _tile) : RFDCTile(_rfdc, XRFDC_ADC_TILE, _tile)
  {    
    rfdc_func(XRFdc_SetupFIFO, 1);
  }

  DACTile::DACTile(RFDC &_rfdc, int _tile) : RFDCTile(_rfdc, XRFDC_DAC_TILE, _tile)
  {    
  }
};						  

