#pragma once

#include <cstdint>
#include <map>

namespace piradio
{
  class LMX2594Config
  {
  public:
    std::uint16_t powerdown;
    std::uint16_t reset;
    std::uint16_t muxout_ld_sel;
    std::uint16_t fcal_en;
    std::uint16_t fcal_lpfd_adj;
    std::uint16_t fcal_hpfd_adj;
    std::uint16_t out_mute;
    std::uint16_t vco_phase_sync;
    std::uint16_t ramp_en;
    std::uint16_t cal_clk_div;
    std::uint16_t acal_cmp_dly;
    std::uint16_t out_force;
    std::uint16_t vco_capctrl_force;
    std::uint16_t vco_daciset_force;
    std::uint16_t osc_2x;
    std::uint16_t mult;
    std::uint16_t pll_r;
    std::uint16_t pll_r_pre;
    std::uint16_t cpg;
    std::uint16_t vco_daciset;
    std::uint16_t vco_daciset_strt;
    std::uint16_t vco_capctrl;
    std::uint16_t vco_sel_force;
    std::uint16_t vco_sel;
    std::uint16_t seg1_en;
    std::uint32_t pll_n;
    std::uint16_t pfd_dly_sel;
    std::uint16_t mash_seed_en;
    std::uint64_t pll_den;
    std::uint64_t mash_seed;
    std::uint64_t pll_num;
    std::uint16_t mash_order;
    std::uint16_t mash_reset_n;
    std::uint16_t outa_pd;
    std::uint16_t outb_pd;
    std::uint16_t outa_pwr;
    std::uint16_t outb_pwr;
    std::uint16_t out_iset;
    std::uint16_t outa_mux;
    std::uint16_t outb_mux;
    std::uint16_t inpin_fmt;
    std::uint16_t inpin_lvl;
    std::uint16_t inpin_hyst;
    std::uint16_t inpin_ignore;
    std::uint16_t ld_type;
    std::uint32_t ld_dly;
    std::uint64_t mash_rst_count;
    std::uint16_t sysref_repeat;
    std::uint16_t sysref_en;
    std::uint16_t sysref_pulse;
    std::uint16_t sysref_div_pre;
    std::uint16_t sysref_div;
    std::uint16_t jesd_dac1_ctrl;
    std::uint16_t jesd_dac2_ctrl;
    std::uint16_t jesd_dac3_ctrl;
    std::uint16_t jesd_dac4_ctrl;
    std::uint16_t sysref_pulse_cnt;
    std::uint16_t chdiv;
    std::uint16_t vco_capctrl_strt;
    std::uint16_t quick_recal_en;
    std::uint16_t ramp_trig_cal;
    std::uint64_t ramp_thresh;
    std::uint64_t ramp_limit_high;
    std::uint64_t ramp_limit_low;
    std::uint16_t ramp_burst_count;
    std::uint16_t ramp_burst_en;
    std::uint16_t ramp_burst_trig;
    std::uint16_t ramp_triga;
    std::uint16_t ramp_trigb;
    std::uint16_t ramp0_dly;
    std::uint16_t ramp0_rst;
    std::uint32_t ramp0_inc;
    std::uint32_t ramp0_len;
    std::uint16_t ramp0_next;
    std::uint16_t ramp0_next_trig;
    std::uint16_t ramp1_dly;
    std::uint16_t ramp1_rst;
    std::uint32_t ramp1_inc;
    std::uint32_t ramp1_len;
    std::uint16_t ramp1_next;
    std::uint16_t ramp1_next_trig;
    std::uint16_t ramp_dly_cnt;
    std::uint16_t ramp_manual;
    std::uint16_t ramp_scale_cnt;
    std::uint16_t rb_vco_sel;
    std::uint16_t rb_ld_vtune;
    std::uint16_t rb_vco_capctrl;
    std::uint16_t rb_vco_daciset;

    LMX2594Config();
    void fill_regs(std::map<int, std::uint16_t> &map);
    void read_regs(const std::map<int, std::uint16_t> &map);
    void dump(void) const;
    void dump_compare(const LMX2594Config &other) const;
  };
};
