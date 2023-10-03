#pragma once

#include <string>
#include <stdexcept>
#include <iostream>

#include <piradio/rfdc.hpp>
#include <piradio/frequency.hpp>
    

namespace piradio
{
  class RFDCTile;
  
  class RFDCPLL
  {
    bool enabled() const;
    
  protected:
    friend class RFDCTile;
    
    RFDCPLL(RFDCTile &_tile);

    XRFdc_PLL_Settings settings() const;
    
    RFDCTile &tile;
  };
  
  class RFDCTile
  {
  public:
    RFDCPLL pll;

    template <typename F, class... types> int rfdc_func(F f, types... args)
    {
      return f(&rfdc.rfdc, type, tile, args...);
    }

    template <typename F, class... types> int rfdc_func_no_type(F f, types... args)
    {
      return f(&rfdc.rfdc, tile, args...);
    }

    int update_tile(int evt)
    {
      return rfdc_func(XRFdc_UpdateEvent, 0, evt);
    }

    int tile_no(void) { return tile; }

    int reset(void) { return rfdc_func(XRFdc_Reset); }

    bool enabled();
    
    bool pll_locked(void) {
      int result;
      u32 locked;

      result = rfdc_func(XRFdc_GetPLLLockStatus, &locked);

      if (result != XRFDC_SUCCESS) {
	throw std::runtime_error("Unable to get lock status");
      }

      return locked == XRFDC_PLL_LOCKED;
    }

    frequency ref_clk_freq(void) {
      int result;
      u32 locked;

      XRFdc_PLL_Settings s;
      
      result = rfdc_func(XRFdc_GetPLLConfig, &s);

      return MHz(s.RefClkFreq);
    }
    
    std::string get_id_string() { return id_string; }
    
  protected:
    RFDC &rfdc;
    int type, tile;
    const std::string id_string;

    RFDCTile(RFDC &_rfdc, int _type, int _tile);
  };

  class ADCTile : public RFDCTile
  {
  public:
    ADCTile(RFDC &_rfdc, int _tile);

  protected:
  };

  class DACTile : public RFDCTile
  {
  public:
    DACTile(RFDC &_rfdc, int _tile);

  protected:
  };
};
