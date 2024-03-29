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

    XRFdc_PLL_Settings pll_settings(void) {
      int result;
      
      XRFdc_PLL_Settings s;
      
      result = rfdc_func(XRFdc_GetPLLConfig, &s);

      // TODO: Check and throw a sane exception
      
      return s;
    }
    
    frequency sample_freq(void) {
      return GHz(pll_settings().SampleRate);
    }
    
    frequency ref_clk_freq(void) {
      return MHz(pll_settings().RefClkFreq);
    }
    
    std::string get_id_string() { return id_string; }

    inline u64 read64(u32 addr) { return rfdc.read64(reg_offset + addr); }
    inline u32 read32(u32 addr) { return rfdc.read32(reg_offset + addr); }
    inline u16 read16(u32 addr) { return rfdc.read16(reg_offset + addr); }
    inline u8 read8(u32 addr) { return rfdc.read8(reg_offset + addr); }

    inline u64 read_drp64(u32 addr) { return rfdc.read64(drp_offset + addr); }
    inline u32 read_drp32(u32 addr) { return rfdc.read32(drp_offset + addr); }
    inline u16 read_drp16(u32 addr) { return rfdc.read16(drp_offset + addr); }
    inline u8 read_drp8(u32 addr) { return rfdc.read8(drp_offset + addr); }

    inline void write64(u32 addr, u64 v) { rfdc.write64(reg_offset + addr, v); }
    inline void write32(u32 addr, u32 v) { rfdc.write32(reg_offset + addr, v); }
    inline void write16(u32 addr, u16 v) { rfdc.write16(reg_offset + addr, v); }
    inline void write8(u32 addr, u8 v) { rfdc.write8(reg_offset + addr, v); }

    inline void write_drp64(u32 addr, u64 v) { rfdc.write64(drp_offset + addr, v); }
    inline void write_drp32(u32 addr, u32 v) { rfdc.write32(drp_offset + addr, v); }
    inline void write_drp16(u32 addr, u16 v) { rfdc.write16(drp_offset + addr, v); }
    inline void write_drp8(u32 addr, u8 v) { rfdc.write8(drp_offset + addr, v); }

    
  protected:
    RFDC &rfdc;
    int type, tile;
    u32 reg_offset;
    u32 drp_offset;
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
  private:
  };
};
