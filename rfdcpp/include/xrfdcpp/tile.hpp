#pragma once

#include <stdint.h>

#include <tuple>

#include <magic_enum.hpp>

#include <xrfdcpp/config.hpp>
#include <xrfdcpp/regs.hpp>
#include <xrfdcpp/types.hpp>
#include <xrfdcpp/frequency.hpp>


namespace rfdc {
  template <class config_type, class csr_type> struct tile_params
  {
    RFDC &dc;
    volatile csr_type *csr;
    const config_type &config;
    const int n_tile;

    tile_params(RFDC &_dc,
		int _n,
		const config_type &_config,
		volatile csr_type *_csr) : dc(_dc),
					    csr(_csr),
					    n_tile(_n),
					    config(_config)
    {
    }
  };

  template <class config_type, class csr_type> class Tile;

  template <class config_type, class csr_type> class TilePLL
  {
    Tile<config_type, csr_type> &tile;

  public:
    
  }

  
  template <class config_type, class csr_type> class TileClock
  {
    Tile<config_type, csr_type> &tile;
    
  public:
    TileClock(Tile<config_type, csr_type> &_tile) : tile(_tile) {
    };

    dfrequency sample_rate(void) {
      return dfrequency::GHz(tile.config.sample_rate);
    }

    dfrequency reference(void) {
      return dfrequency::MHz(tile.config.ref_clk_freq);
    }

    dfrequency fabric(void) {
      return dfrequency::MHz(tile.config.fab_clk_freq);
    }

    dfrequency output() {
      return sample_rate() / output_div();
    }
    
    uint32_t reference_div() {
      return tile.config.ref_clk_div;
    }
    
    uint32_t output_div() {
      return tile.config.output_div;
    }
  };
  
  template <class config_type, class csr_type> class Tile
  {
    friend class TilePLL<config_type, csr_type>;
    friend class TileClock<config_type, csr_type>;
    
  protected:
    volatile csr_type *csr;
  public:
    RFDC &dc;
    const config_type &config;
    const int n_tile;

    TileClock<config_type, csr_type> clock;
    
    Tile(const tile_params<config_type, csr_type> &p) : dc(p.dc),
							csr(p.csr),
							n_tile(p.n_tile),
							config(p.config),
							clock(*this)
    {
    }
    
    uint32_t state() {
      return csr->t.current_state;
    }
    
    bool cdetect_status() {
      return (csr->t.clock_detect & 1) ? true : false;
    }
    
    bool clock_detected() {
      return (csr->t.common_status & 1) ? true : false;
    }
    
    bool supplies_up() {
      return (csr->t.common_status & 2) ? true : false;
    }
    
    bool power_up() {
      return (csr->t.common_status & 4) ? true : false;
    }
    
    bool pll_locked() {
      return (csr->t.common_status & 8) ? true : false;
    }
    
    cfg::multiband_mode get_multiband_mode() {
      return *magic_enum::enum_cast<cfg::multiband_mode>(config.multiband);
    }

    virtual uint32_t get_path_enabled_reg(void) = 0;

    uint32_t get_analog_enabled() { return get_path_enabled_reg() & 0xFFFF; }
    uint32_t get_digital_enabled() { return (get_path_enabled_reg() >> 16) & 0xFFFF; }
    
    uint32_t get_digital_enabled_slices(void) {
      return (get_digital_enabled() >> 4*n_tile) & 0xF;
    }

    uint32_t get_analog_enabled_slices(void) {
      return (get_analog_enabled() >> 4*n_tile) & 0xF;
    }
  };
};
