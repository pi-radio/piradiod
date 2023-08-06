#pragma once

#include <cstdint>
#include <map>

namespace piradio
{
  class LMX2820Config
  {
    std::uint16_t powerdown;
    std::uint16_t reset;
    std::uint16_t fcal_en;
    std::uint16_t dblr_cal_en;
    std::uint16_t fcal_lpfd_adj;
    std::uint16_t fcal_hpfd_adj;
    std::uint16_t instcal_skip_acal;
    std::uint16_t instcal_en;
    std::uint16_t instcal_dblr_en;
    std::uint16_t ld_vtune_en;
    std::uint16_t phase_sync_en;
    std::uint16_t quick_recal_en;
    std::uint16_t instcal_dly;
    std::uint16_t cal_clk_div;
    std::uint16_t acal_cmp_dly;
    std::uint16_t vco_capctrl_force;
    std::uint16_t vco_daciset_force;
    std::uint16_t pfd_dly_manual;
    std::uint16_t osc_2x;
    std::uint16_t mult;
    std::uint16_t pll_r;
    std::uint16_t pll_r_pre;
    std::uint16_t pfd_single;
    std::uint16_t pfd_pol;
    std::uint16_t cpg;
    std::uint16_t ld_type;
    std::uint32_t ld_dly;
    std::uint16_t tempsense_en;
    std::uint16_t vco_daciset;
    std::uint16_t vco_capctrl;
    std::uint16_t vco_sel;
    std::uint16_t vco_sel_force;
    std::uint16_t chdiva;
    std::uint16_t chdivb;
    std::uint16_t extvco_en;
    std::uint16_t extvco_div;
    std::uint16_t loopback_en;
    std::uint16_t mashseed_en;
    std::uint16_t mash_order;
    std::uint16_t mash_reset_n;
    std::uint16_t pll_n;
    std::uint16_t pfd_dly;
    std::uint64_t pll_den;
    std::uint64_t mash_seed;
    std::uint64_t pll_num;
    std::uint64_t instcal_pll_num;
    std::uint16_t extpfd_div;
    std::uint16_t pfd_sel;
    std::uint64_t mash_rst_count;
    std::uint16_t sysref_repeat;
    std::uint16_t sysref_en;
    std::uint16_t sysref_pulse;
    std::uint16_t sysref_repeat_ns;
    std::uint16_t sysref_div_pre;
    std::uint16_t sysref_inp_fmt;
    std::uint16_t sysref_div;
    std::uint16_t jesd_dac1_ctrl;
    std::uint16_t jesd_dac2_ctrl;
    std::uint16_t jesd_dac3_ctrl;
    std::uint16_t jesd_dac4_ctrl;
    std::uint16_t sysref_pulse_cnt;
    std::uint16_t psync_inp_fmt;
    std::uint16_t inpin_ignore;
    std::uint16_t srout_pd;
    std::uint16_t dblbuf_pll_en;
    std::uint16_t dblbuf_chdiv_en;
    std::uint16_t dblbuf_outbuf_en;
    std::uint16_t dblbuf_outmux_en;
    std::uint16_t rb_vco_sel;
    std::uint16_t rb_vco_capctrl;
    std::uint16_t rb_ld;
    std::uint16_t rb_vco_daciset;
    std::uint16_t rb_temp_sens;
    std::uint16_t pinmute_pol;
    std::uint16_t outa_mux;
    std::uint16_t outa_pd;
    std::uint16_t outa_pwr;
    std::uint16_t outb_mux;
    std::uint16_t outb_pd;
    std::uint16_t outb_pwr;

    void fill_regs(std::map<int, std::uint16_t> &map);
    void read_regs(const std::map<int, std::uint16_t> &map);
    void dump(void);
  };
};
