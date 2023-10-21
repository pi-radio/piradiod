#include <piradio/lmx2594_config.hpp>
#include <iostream>
namespace piradio
{
  LMX2594Config::LMX2594Config()
  {
    powerdown = 0;
    reset = 0;
    muxout_ld_sel = 0;
    fcal_en = 0;
    fcal_lpfd_adj = 0;
    fcal_hpfd_adj = 0;
    out_mute = 0;
    vco_phase_sync = 0;
    ramp_en = 0;
    cal_clk_div = 0;
    acal_cmp_dly = 0;
    out_force = 0;
    vco_capctrl_force = 0;
    vco_daciset_force = 0;
    osc_2x = 0;
    mult = 0;
    pll_r = 0;
    pll_r_pre = 0;
    cpg = 0;
    vco_daciset = 0;
    vco_daciset_strt = 0;
    vco_capctrl = 0;
    vco_sel_force = 0;
    vco_sel = 0;
    seg1_en = 0;
    pll_n = 0;
    pll_n = 0;
    pfd_dly_sel = 0;
    mash_seed_en = 0;
    pll_den = 0;
    pll_den = 0;
    mash_seed = 0;
    mash_seed = 0;
    pll_num = 0;
    pll_num = 0;
    mash_order = 0;
    mash_reset_n = 0;
    outa_pd = 0;
    outb_pd = 0;
    outa_pwr = 0;
    outb_pwr = 0;
    out_iset = 0;
    outa_mux = 0;
    outb_mux = 0;
    inpin_fmt = 0;
    inpin_lvl = 0;
    inpin_hyst = 0;
    inpin_ignore = 0;
    ld_type = 0;
    ld_dly = 0;
    mash_rst_count = 0;
    mash_rst_count = 0;
    sysref_repeat = 0;
    sysref_en = 0;
    sysref_pulse = 0;
    sysref_div_pre = 0;
    sysref_div = 0;
    jesd_dac1_ctrl = 0;
    jesd_dac2_ctrl = 0;
    jesd_dac3_ctrl = 0;
    jesd_dac4_ctrl = 0;
    sysref_pulse_cnt = 0;
    chdiv = 0;
    vco_capctrl_strt = 0;
    quick_recal_en = 0;
    ramp_trig_cal = 0;
    ramp_thresh = 0;
    ramp_thresh = 0;
    ramp_thresh = 0;
    ramp_limit_high = 0;
    ramp_limit_high = 0;
    ramp_limit_high = 0;
    ramp_limit_low = 0;
    ramp_limit_low = 0;
    ramp_limit_low = 0;
    ramp_burst_count = 0;
    ramp_burst_en = 0;
    ramp_burst_trig = 0;
    ramp_triga = 0;
    ramp_trigb = 0;
    ramp0_dly = 0;
    ramp0_rst = 0;
    ramp0_inc = 0;
    ramp0_inc = 0;
    ramp0_len = 0;
    ramp0_next = 0;
    ramp0_next_trig = 0;
    ramp1_dly = 0;
    ramp1_rst = 0;
    ramp1_inc = 0;
    ramp1_inc = 0;
    ramp1_len = 0;
    ramp1_next = 0;
    ramp1_next_trig = 0;
    ramp_dly_cnt = 0;
    ramp_manual = 0;
    ramp_scale_cnt = 0;
    rb_vco_sel = 0;
    rb_ld_vtune = 0;
    rb_vco_capctrl = 0;
    rb_vco_daciset = 0;
  }

  void LMX2594Config::fill_regs(std::map<int, uint16_t> &reg_vals)
  {
    reg_vals[0] = 0x2410 | (powerdown & 0x1) | ((reset & 0x1) << 1) | ((muxout_ld_sel & 0x1) << 2) | ((fcal_en & 0x1) << 3) | ((fcal_lpfd_adj & 0x3) << 5) | ((fcal_hpfd_adj & 0x3) << 7) | ((out_mute & 0x1) << 9) | ((vco_phase_sync & 0x1) << 14) | ((ramp_en & 0x1) << 15);
    reg_vals[1] = 0x0808 | (cal_clk_div & 0x7);

    reg_vals[2] = 0x0500;
    reg_vals[3] = 0x0642;
    
    reg_vals[4] = 0x0043 | ((acal_cmp_dly & 0xff) << 8);

    reg_vals[5] = 0x00C8;
    reg_vals[6] = 0xC802;
    
    reg_vals[7] = 0x00b2 | ((out_force & 0x1) << 14);
    reg_vals[8] = 0x2000 | ((vco_capctrl_force & 0x1) << 11) | ((vco_daciset_force & 0x1) << 14);
    reg_vals[9] = 0x0604 | ((osc_2x & 0x1) << 12);
    reg_vals[10] = 0x1058 | ((mult & 0x1f) << 7);
    reg_vals[11] = 0x0008 | ((pll_r & 0xff) << 4);
    reg_vals[12] = 0x5000 | (pll_r_pre & 0xff);

    reg_vals[13] = 0x4000;
    
    reg_vals[14] = 0x1e00 | ((cpg & 0x7) << 4);

    reg_vals[15] = 0x064F;
    
    reg_vals[16] = 0x0000 | (vco_daciset & 0x1ff);
    reg_vals[17] = 0x0000 | (vco_daciset_strt & 0x1ff);

    reg_vals[18] = 0x0064;
    
    reg_vals[19] = 0x2700 | (vco_capctrl & 0xff);
    reg_vals[20] = 0xc048 | ((vco_sel_force & 0x1) << 10) | ((vco_sel & 0x7) << 11);

    reg_vals[21] = 0x0401;
    reg_vals[22] = 0x0001;
    reg_vals[23] = 0x007C;
    reg_vals[24] = 0x071A;
    reg_vals[25] = 0x0C2B;
    // Value from ZCU111 programming stuff
    reg_vals[25] = 0x0624;
    reg_vals[26] = 0x0DB0;
    reg_vals[27] = 0x0002;
    reg_vals[28] = 0x0488;
    reg_vals[29] = 0x318C;
    reg_vals[30] = 0x318C;
    
    reg_vals[31] = 0x03ec | ((seg1_en & 0x1) << 14);

    reg_vals[32] = 0x0393;
    reg_vals[33] = 0x1E21;
    
    reg_vals[34] = 0x0000 | ((pll_n >> 16) & 0x3fff);

    reg_vals[35] = 0x0004;
    
    reg_vals[36] = 0x0000 | (pll_n & 0xffff);
    reg_vals[37] = 0x0004 | ((pfd_dly_sel & 0x3f) << 8) | ((mash_seed_en & 0x1) << 15);
    reg_vals[38] = 0x0000 | ((pll_den >> 16) & 0x1);
    reg_vals[39] = 0x0000 | (pll_den & 0xffff);
    reg_vals[40] = 0x0000 | ((mash_seed >> 16) & 0x1);
    reg_vals[41] = 0x0000 | (mash_seed & 0xffff);
    reg_vals[42] = 0x0000 | ((pll_num >> 16) & 0x1);
    reg_vals[43] = 0x0000 | (pll_num & 0xffff);
    reg_vals[44] = 0x0000 | (mash_order & 0x7) | ((mash_reset_n & 0x1) << 5) | ((outa_pd & 0x1) << 6) | ((outb_pd & 0x1) << 7) | ((outa_pwr & 0x3f) << 8);
    reg_vals[45] = 0xc0c0 | (outb_pwr & 0x3f) | ((out_iset & 0x3) << 9) | ((outa_mux & 0x3) << 11);
    reg_vals[46] = 0x07fc | (outb_mux & 0x3);

    reg_vals[47] = 0x0300;
    reg_vals[48] = 0x0300;
    reg_vals[49] = 0x4180;
    reg_vals[50] = 0x0000;
    reg_vals[51] = 0x0080;
    reg_vals[52] = 0x0820;
    reg_vals[53] = 0x0000;
    reg_vals[54] = 0x0000;
    reg_vals[55] = 0x0000;
    reg_vals[56] = 0x0000;
    reg_vals[57] = 0x0020;
    reg_vals[58] = 0x9001;    
    
    reg_vals[58] = 0x0001 | ((inpin_fmt & 0x7) << 9) | ((inpin_lvl & 0x3) << 12) | ((inpin_hyst & 0x1) << 14) | ((inpin_ignore & 0x1) << 15);
    reg_vals[59] = 0x0000 | (ld_type & 0x1);
    reg_vals[60] = 0x0000 | (ld_dly & 0xffff);

    reg_vals[61] = 0x00a8;
    reg_vals[62] = 0x0322;
    reg_vals[63] = 0x0000;
    reg_vals[64] = 0x1388;
    reg_vals[65] = 0x0000;
    reg_vals[66] = 0x01f4;
    reg_vals[67] = 0x0000;
    reg_vals[68] = 0x03e8;
    
    reg_vals[69] = 0x0000 | ((mash_rst_count >> 16) & 0x1);
    reg_vals[70] = 0x0000 | (mash_rst_count & 0xffff);
    reg_vals[71] = 0x0001 | ((sysref_repeat & 0x1) << 2) | ((sysref_en & 0x1) << 3) | ((sysref_pulse & 0x1) << 4) | ((sysref_div_pre & 0x7) << 5);
    reg_vals[72] = 0x0000 | (sysref_div & 0x7ff);
    reg_vals[73] = 0x0000 | (jesd_dac1_ctrl & 0x3f) | ((jesd_dac2_ctrl & 0x3f) << 6);
    reg_vals[74] = 0x0000 | (jesd_dac3_ctrl & 0x3f) | ((jesd_dac4_ctrl & 0x3f) << 6) | ((sysref_pulse_cnt & 0xf) << 12);
    reg_vals[75] = 0x0800 | ((chdiv & 0x1f) << 6);

    reg_vals[76] = 0x000c;
    reg_vals[77] = 0x0000;
    
    reg_vals[78] = 0x0001 | ((vco_capctrl_strt & 0xff) << 1) | ((quick_recal_en & 0x1) << 9) | ((ramp_thresh >> 32) & 0xffff);
    reg_vals[79] = 0x0000 | ((ramp_thresh >> 16) & 0xFFFF);
    reg_vals[80] = 0x0000 | (ramp_thresh & 0xffff);
    reg_vals[81] = 0x0000 | ((ramp_limit_high >> 32) & 0x1);
    reg_vals[82] = 0x0000 | ((ramp_limit_high >> 16) & 0xffff);
    reg_vals[83] = 0x0000 | (ramp_limit_high & 0xffff);
    reg_vals[84] = 0x0000 | ((ramp_limit_low >> 32) & 0x1);
    reg_vals[85] = 0x0000 | ((ramp_limit_low >> 16) & 0xffff);
    reg_vals[86] = 0x0000 | (ramp_limit_low & 0xffff);

    reg_vals[87] = 0x0000;
    reg_vals[88] = 0x0000;
    reg_vals[89] = 0x0000;
    reg_vals[90] = 0x0000;
    reg_vals[91] = 0x0000;
    reg_vals[92] = 0x0000;
    reg_vals[93] = 0x0000;
    reg_vals[94] = 0x0000;
    reg_vals[95] = 0x0000;
    
    reg_vals[96] = 0x0000 | ((ramp_burst_count & 0x1fff) << 2) | ((ramp_burst_en & 0x1) << 15);
    reg_vals[97] = 0x0800 | (ramp_burst_trig & 0x3) | ((ramp_triga & 0xf) << 3) | ((ramp_trigb & 0xf) << 7) | ((ramp0_rst & 0x1) << 15);
    reg_vals[98] = 0x0000 | (ramp0_dly & 0x1) | ((ramp0_inc >> 16) & 0x3FFF);
    reg_vals[99] = 0x0000 | (ramp0_inc & 0xffff);
    reg_vals[100] = 0x0000 | (ramp0_len & 0xffff);
    reg_vals[101] = 0x0000 | ((ramp0_next & 0x1) << 4) | (ramp0_next_trig & 0x3) | ((ramp1_dly & 0x1) << 6) | ((ramp1_rst & 0x1) << 5);
    reg_vals[102] = 0x0000 | ((ramp1_inc >> 16) & 0x3FFF);
    reg_vals[103] = 0x0000 | (ramp1_inc & 0xffff);
    reg_vals[104] = 0x0000 | (ramp1_len & 0xffff);
    reg_vals[105] = 0x0000 | ((ramp1_next & 0x1) << 4) | (ramp1_next_trig & 0x3) | ((ramp_dly_cnt & 0x3ff) << 6) | ((ramp_manual & 0x1) << 5);
    reg_vals[106] = 0x0000 | ((ramp_trig_cal & 0x1) << 4) | (ramp_scale_cnt & 0x7);

    reg_vals[107] = 0x0000;
    reg_vals[108] = 0x0000;
    reg_vals[109] = 0x0000;
    
    reg_vals[110] = 0x0000 | ((rb_vco_sel & 0x7) << 5) | ((rb_ld_vtune & 0x3) << 9);
    reg_vals[111] = 0x0000 | (rb_vco_capctrl & 0xff);
    reg_vals[112] = 0x0000 | (rb_vco_daciset & 0x1ff);
  }

  void LMX2594Config::read_regs(const std::map<int, std::uint16_t> &reg_vals)
  {
    powerdown = reg_vals.at(0) & 0x1;
    reset = (reg_vals.at(0) >> 1) & 0x1;
    muxout_ld_sel = (reg_vals.at(0) >> 2) & 0x1;
    fcal_en = (reg_vals.at(0) >> 3) & 0x1;
    fcal_lpfd_adj = (reg_vals.at(0) >> 5) & 0x3;
    fcal_hpfd_adj = (reg_vals.at(0) >> 7) & 0x3;
    out_mute = (reg_vals.at(0) >> 9) & 0x1;
    vco_phase_sync = (reg_vals.at(0) >> 14) & 0x1;
    ramp_en = (reg_vals.at(0) >> 15) & 0x1;
    cal_clk_div = reg_vals.at(1) & 0x7;
    acal_cmp_dly = (reg_vals.at(4) >> 8) & 0xff;
    out_force = (reg_vals.at(7) >> 14) & 0x1;
    vco_capctrl_force = (reg_vals.at(8) >> 11) & 0x1;
    vco_daciset_force = (reg_vals.at(8) >> 14) & 0x1;
    osc_2x = (reg_vals.at(9) >> 12) & 0x1;
    mult = (reg_vals.at(10) >> 7) & 0x1f;
    pll_r = (reg_vals.at(11) >> 4) & 0xff;
    pll_r_pre = reg_vals.at(12) & 0xff;
    cpg = (reg_vals.at(14) >> 4) & 0x7;
    vco_daciset = reg_vals.at(16) & 0x1ff;
    vco_daciset_strt = reg_vals.at(17) & 0x1ff;
    vco_capctrl = reg_vals.at(19) & 0xff;
    vco_sel_force = (reg_vals.at(20) >> 10) & 0x1;
    vco_sel = (reg_vals.at(20) >> 11) & 0x7;
    seg1_en = (reg_vals.at(31) >> 14) & 0x1;
    pll_n = ((uint32_t)reg_vals.at(31) << 16) & 0x7;
    pll_n = reg_vals.at(36) & 0xffff;
    pfd_dly_sel = (reg_vals.at(37) >> 8) & 0x3f;
    mash_seed_en = (reg_vals.at(37) >> 15) & 0x1;
    pll_den = ((uint32_t)reg_vals.at(37) << 16) & 0xffff;
    pll_den = reg_vals.at(39) & 0xffff;
    mash_seed = ((uint32_t)reg_vals.at(39) << 16) & 0xffff;
    mash_seed = reg_vals.at(41) & 0xffff;
    pll_num = ((uint32_t)reg_vals.at(41) << 16) & 0xffff;
    pll_num = reg_vals.at(43) & 0xffff;
    mash_order = reg_vals.at(44) & 0x7;
    mash_reset_n = (reg_vals.at(44) >> 5) & 0x1;
    outa_pd = (reg_vals.at(44) >> 6) & 0x1;
    outb_pd = (reg_vals.at(44) >> 7) & 0x1;
    outa_pwr = (reg_vals.at(44) >> 8) & 0x3f;
    outb_pwr = reg_vals.at(45) & 0x3f;
    out_iset = (reg_vals.at(45) >> 9) & 0x3;
    outa_mux = (reg_vals.at(45) >> 11) & 0x3;
    outb_mux = reg_vals.at(46) & 0x3;
    inpin_fmt = (reg_vals.at(58) >> 9) & 0x7;
    inpin_lvl = (reg_vals.at(58) >> 12) & 0x3;
    inpin_hyst = (reg_vals.at(58) >> 14) & 0x1;
    inpin_ignore = (reg_vals.at(58) >> 15) & 0x1;
    ld_type = reg_vals.at(59) & 0x1;
    ld_dly = reg_vals.at(60) & 0xffff;
    mash_rst_count = ((uint32_t)reg_vals.at(60) << 16) & 0xffff;
    mash_rst_count = reg_vals.at(70) & 0xffff;
    sysref_repeat = (reg_vals.at(71) >> 2) & 0x1;
    sysref_en = (reg_vals.at(71) >> 3) & 0x1;
    sysref_pulse = (reg_vals.at(71) >> 4) & 0x1;
    sysref_div_pre = (reg_vals.at(71) >> 5) & 0x7;
    sysref_div = reg_vals.at(72) & 0x7ff;
    jesd_dac1_ctrl = reg_vals.at(73) & 0x3f;
    jesd_dac2_ctrl = (reg_vals.at(73) >> 6) & 0x3f;
    jesd_dac3_ctrl = reg_vals.at(74) & 0x3f;
    jesd_dac4_ctrl = (reg_vals.at(74) >> 6) & 0x3f;
    sysref_pulse_cnt = (reg_vals.at(74) >> 12) & 0xf;
    chdiv = (reg_vals.at(75) >> 6) & 0x1f;
    vco_capctrl_strt = (reg_vals.at(78) >> 1) & 0xff;
    quick_recal_en = (reg_vals.at(78) >> 9) & 0x1;
    ramp_trig_cal = (reg_vals.at(106) >> 4) & 0x1;
    ramp_thresh = ((uint32_t)reg_vals.at(106) << 21) & 0x1;
    ramp_thresh = ((uint32_t)reg_vals.at(106) << 16) & 0xffff;
    ramp_thresh = reg_vals.at(80) & 0xffff;
    ramp_limit_high = ((uint64_t)reg_vals.at(80) << 32) & 0x1;
    ramp_limit_high = ((uint32_t)reg_vals.at(80) << 16) & 0xffff;
    ramp_limit_high = reg_vals.at(83) & 0xffff;
    ramp_limit_low = ((uint64_t)reg_vals.at(83) << 32) & 0x1;
    ramp_limit_low = ((uint32_t)reg_vals.at(83) << 16) & 0xffff;
    ramp_limit_low = reg_vals.at(86) & 0xffff;
    ramp_burst_count = (reg_vals.at(96) >> 2) & 0x1fff;
    ramp_burst_en = (reg_vals.at(96) >> 15) & 0x1;
    ramp_burst_trig = reg_vals.at(97) & 0x3;
    ramp_triga = (reg_vals.at(97) >> 3) & 0xf;
    ramp_trigb = (reg_vals.at(97) >> 7) & 0xf;
    ramp0_dly = reg_vals.at(98) & 0x1;
    ramp0_rst = (reg_vals.at(97) >> 15) & 0x1;
    ramp0_inc = (reg_vals.at(97) << 14) & 0x3fff;
    ramp0_inc = reg_vals.at(99) & 0xffff;
    ramp0_len = reg_vals.at(100) & 0xffff;
    ramp0_next = (reg_vals.at(101) >> 4) & 0x1;
    ramp0_next_trig = reg_vals.at(101) & 0x3;
    ramp1_dly = (reg_vals.at(101) >> 6) & 0x1;
    ramp1_rst = (reg_vals.at(101) >> 5) & 0x1;
    ramp1_inc = ((uint32_t)reg_vals.at(101) << 16) & 0x3fff;
    ramp1_inc = reg_vals.at(103) & 0xffff;
    ramp1_len = reg_vals.at(104) & 0xffff;
    ramp1_next = (reg_vals.at(105) >> 4) & 0x1;
    ramp1_next_trig = reg_vals.at(105) & 0x3;
    ramp_dly_cnt = (reg_vals.at(105) >> 6) & 0x3ff;
    ramp_manual = (reg_vals.at(105) >> 5) & 0x1;
    ramp_scale_cnt = reg_vals.at(106) & 0x7;
    rb_vco_sel = (reg_vals.at(110) >> 5) & 0x7;
    rb_ld_vtune = (reg_vals.at(110) >> 9) & 0x3;
    rb_vco_capctrl = reg_vals.at(111) & 0xff;
    rb_vco_daciset = reg_vals.at(112) & 0x1ff;
  }

  void LMX2594Config::dump(void) const
  {
    std::cout << "powerdown: " << powerdown << std::endl;
    std::cout << "reset: " << reset << std::endl;
    std::cout << "muxout_ld_sel: " << muxout_ld_sel << std::endl;
    std::cout << "fcal_en: " << fcal_en << std::endl;
    std::cout << "fcal_lpfd_adj: " << fcal_lpfd_adj << std::endl;
    std::cout << "fcal_hpfd_adj: " << fcal_hpfd_adj << std::endl;
    std::cout << "out_mute: " << out_mute << std::endl;
    std::cout << "vco_phase_sync: " << vco_phase_sync << std::endl;
    std::cout << "ramp_en: " << ramp_en << std::endl;
    std::cout << "cal_clk_div: " << cal_clk_div << std::endl;
    std::cout << "acal_cmp_dly: " << acal_cmp_dly << std::endl;
    std::cout << "out_force: " << out_force << std::endl;
    std::cout << "vco_capctrl_force: " << vco_capctrl_force << std::endl;
    std::cout << "vco_daciset_force: " << vco_daciset_force << std::endl;
    std::cout << "osc_2x: " << osc_2x << std::endl;
    std::cout << "mult: " << mult << std::endl;
    std::cout << "pll_r: " << pll_r << std::endl;
    std::cout << "pll_r_pre: " << pll_r_pre << std::endl;
    std::cout << "cpg: " << cpg << std::endl;
    std::cout << "vco_daciset: " << vco_daciset << std::endl;
    std::cout << "vco_daciset_strt: " << vco_daciset_strt << std::endl;
    std::cout << "vco_capctrl: " << vco_capctrl << std::endl;
    std::cout << "vco_sel_force: " << vco_sel_force << std::endl;
    std::cout << "vco_sel: " << vco_sel << std::endl;
    std::cout << "seg1_en: " << seg1_en << std::endl;
    std::cout << "pll_n: " << pll_n << std::endl;
    std::cout << "pfd_dly_sel: " << pfd_dly_sel << std::endl;
    std::cout << "mash_seed_en: " << mash_seed_en << std::endl;
    std::cout << "pll_den: " << pll_den << std::endl;
    std::cout << "mash_seed: " << mash_seed << std::endl;
    std::cout << "pll_num: " << pll_num << std::endl;
    std::cout << "mash_order: " << mash_order << std::endl;
    std::cout << "mash_reset_n: " << mash_reset_n << std::endl;
    std::cout << "outa_pd: " << outa_pd << std::endl;
    std::cout << "outb_pd: " << outb_pd << std::endl;
    std::cout << "outa_pwr: " << outa_pwr << std::endl;
    std::cout << "outb_pwr: " << outb_pwr << std::endl;
    std::cout << "out_iset: " << out_iset << std::endl;
    std::cout << "outa_mux: " << outa_mux << std::endl;
    std::cout << "outb_mux: " << outb_mux << std::endl;
    std::cout << "inpin_fmt: " << inpin_fmt << std::endl;
    std::cout << "inpin_lvl: " << inpin_lvl << std::endl;
    std::cout << "inpin_hyst: " << inpin_hyst << std::endl;
    std::cout << "inpin_ignore: " << inpin_ignore << std::endl;
    std::cout << "ld_type: " << ld_type << std::endl;
    std::cout << "ld_dly: " << ld_dly << std::endl;
    std::cout << "mash_rst_count: " << mash_rst_count << std::endl;
    std::cout << "sysref_repeat: " << sysref_repeat << std::endl;
    std::cout << "sysref_en: " << sysref_en << std::endl;
    std::cout << "sysref_pulse: " << sysref_pulse << std::endl;
    std::cout << "sysref_div_pre: " << sysref_div_pre << std::endl;
    std::cout << "sysref_div: " << sysref_div << std::endl;
    std::cout << "jesd_dac1_ctrl: " << jesd_dac1_ctrl << std::endl;
    std::cout << "jesd_dac2_ctrl: " << jesd_dac2_ctrl << std::endl;
    std::cout << "jesd_dac3_ctrl: " << jesd_dac3_ctrl << std::endl;
    std::cout << "jesd_dac4_ctrl: " << jesd_dac4_ctrl << std::endl;
    std::cout << "sysref_pulse_cnt: " << sysref_pulse_cnt << std::endl;
    std::cout << "chdiv: " << chdiv << std::endl;
    std::cout << "vco_capctrl_strt: " << vco_capctrl_strt << std::endl;
    std::cout << "quick_recal_en: " << quick_recal_en << std::endl;
    std::cout << "ramp_trig_cal: " << ramp_trig_cal << std::endl;
    std::cout << "ramp_thresh: " << ramp_thresh << std::endl;
    std::cout << "ramp_limit_high: " << ramp_limit_high << std::endl;
    std::cout << "ramp_limit_low: " << ramp_limit_low << std::endl;
    std::cout << "ramp_burst_count: " << ramp_burst_count << std::endl;
    std::cout << "ramp_burst_en: " << ramp_burst_en << std::endl;
    std::cout << "ramp_burst_trig: " << ramp_burst_trig << std::endl;
    std::cout << "ramp_triga: " << ramp_triga << std::endl;
    std::cout << "ramp_trigb: " << ramp_trigb << std::endl;
    std::cout << "ramp0_dly: " << ramp0_dly << std::endl;
    std::cout << "ramp0_rst: " << ramp0_rst << std::endl;
    std::cout << "ramp0_inc: " << ramp0_inc << std::endl;
    std::cout << "ramp0_len: " << ramp0_len << std::endl;
    std::cout << "ramp0_next: " << ramp0_next << std::endl;
    std::cout << "ramp0_next_trig: " << ramp0_next_trig << std::endl;
    std::cout << "ramp1_dly: " << ramp1_dly << std::endl;
    std::cout << "ramp1_rst: " << ramp1_rst << std::endl;
    std::cout << "ramp1_inc: " << ramp1_inc << std::endl;
    std::cout << "ramp1_len: " << ramp1_len << std::endl;
    std::cout << "ramp1_next: " << ramp1_next << std::endl;
    std::cout << "ramp1_next_trig: " << ramp1_next_trig << std::endl;
    std::cout << "ramp_dly_cnt: " << ramp_dly_cnt << std::endl;
    std::cout << "ramp_manual: " << ramp_manual << std::endl;
    std::cout << "ramp_scale_cnt: " << ramp_scale_cnt << std::endl;
    std::cout << "rb_vco_sel: " << rb_vco_sel << std::endl;
    std::cout << "rb_ld_vtune: " << rb_ld_vtune << std::endl;
    std::cout << "rb_vco_capctrl: " << rb_vco_capctrl << std::endl;
    std::cout << "rb_vco_daciset: " << rb_vco_daciset << std::endl;
  }

  void LMX2594Config::dump_compare(const LMX2594Config &other) const
  {
    if (powerdown != other.powerdown) {
      std::cout << "powerdown differs: " << powerdown << " " << other.powerdown << std::endl;
    }
    if (reset != other.reset) {
      std::cout << "reset differs: " << reset << " " << other.reset << std::endl;
    }
    if (muxout_ld_sel != other.muxout_ld_sel) {
      std::cout << "muxout_ld_sel differs: " << muxout_ld_sel << " " << other.muxout_ld_sel << std::endl;
    }
    if (fcal_en != other.fcal_en) {
      std::cout << "fcal_en differs: " << fcal_en << " " << other.fcal_en << std::endl;
    }
    if (fcal_lpfd_adj != other.fcal_lpfd_adj) {
      std::cout << "fcal_lpfd_adj differs: " << fcal_lpfd_adj << " " << other.fcal_lpfd_adj << std::endl;
    }
    if (fcal_hpfd_adj != other.fcal_hpfd_adj) {
      std::cout << "fcal_hpfd_adj differs: " << fcal_hpfd_adj << " " << other.fcal_hpfd_adj << std::endl;
    }
    if (out_mute != other.out_mute) {
      std::cout << "out_mute differs: " << out_mute << " " << other.out_mute << std::endl;
    }
    if (vco_phase_sync != other.vco_phase_sync) {
      std::cout << "vco_phase_sync differs: " << vco_phase_sync << " " << other.vco_phase_sync << std::endl;
    }
    if (ramp_en != other.ramp_en) {
      std::cout << "ramp_en differs: " << ramp_en << " " << other.ramp_en << std::endl;
    }
    if (cal_clk_div != other.cal_clk_div) {
      std::cout << "cal_clk_div differs: " << cal_clk_div << " " << other.cal_clk_div << std::endl;
    }
    if (acal_cmp_dly != other.acal_cmp_dly) {
      std::cout << "acal_cmp_dly differs: " << acal_cmp_dly << " " << other.acal_cmp_dly << std::endl;
    }
    if (out_force != other.out_force) {
      std::cout << "out_force differs: " << out_force << " " << other.out_force << std::endl;
    }
    if (vco_capctrl_force != other.vco_capctrl_force) {
      std::cout << "vco_capctrl_force differs: " << vco_capctrl_force << " " << other.vco_capctrl_force << std::endl;
    }
    if (vco_daciset_force != other.vco_daciset_force) {
      std::cout << "vco_daciset_force differs: " << vco_daciset_force << " " << other.vco_daciset_force << std::endl;
    }
    if (osc_2x != other.osc_2x) {
      std::cout << "osc_2x differs: " << osc_2x << " " << other.osc_2x << std::endl;
    }
    if (mult != other.mult) {
      std::cout << "mult differs: " << mult << " " << other.mult << std::endl;
    }
    if (pll_r != other.pll_r) {
      std::cout << "pll_r differs: " << pll_r << " " << other.pll_r << std::endl;
    }
    if (pll_r_pre != other.pll_r_pre) {
      std::cout << "pll_r_pre differs: " << pll_r_pre << " " << other.pll_r_pre << std::endl;
    }
    if (cpg != other.cpg) {
      std::cout << "cpg differs: " << cpg << " " << other.cpg << std::endl;
    }
    if (vco_daciset != other.vco_daciset) {
      std::cout << "vco_daciset differs: " << vco_daciset << " " << other.vco_daciset << std::endl;
    }
    if (vco_daciset_strt != other.vco_daciset_strt) {
      std::cout << "vco_daciset_strt differs: " << vco_daciset_strt << " " << other.vco_daciset_strt << std::endl;
    }
    if (vco_capctrl != other.vco_capctrl) {
      std::cout << "vco_capctrl differs: " << vco_capctrl << " " << other.vco_capctrl << std::endl;
    }
    if (vco_sel_force != other.vco_sel_force) {
      std::cout << "vco_sel_force differs: " << vco_sel_force << " " << other.vco_sel_force << std::endl;
    }
    if (vco_sel != other.vco_sel) {
      std::cout << "vco_sel differs: " << vco_sel << " " << other.vco_sel << std::endl;
    }
    if (seg1_en != other.seg1_en) {
      std::cout << "seg1_en differs: " << seg1_en << " " << other.seg1_en << std::endl;
    }
    if (pll_n != other.pll_n) {
      std::cout << "pll_n differs: " << pll_n << " " << other.pll_n << std::endl;
    }
    if (pfd_dly_sel != other.pfd_dly_sel) {
      std::cout << "pfd_dly_sel differs: " << pfd_dly_sel << " " << other.pfd_dly_sel << std::endl;
    }
    if (mash_seed_en != other.mash_seed_en) {
      std::cout << "mash_seed_en differs: " << mash_seed_en << " " << other.mash_seed_en << std::endl;
    }
    if (pll_den != other.pll_den) {
      std::cout << "pll_den differs: " << pll_den << " " << other.pll_den << std::endl;
    }
    if (mash_seed != other.mash_seed) {
      std::cout << "mash_seed differs: " << mash_seed << " " << other.mash_seed << std::endl;
    }
    if (pll_num != other.pll_num) {
      std::cout << "pll_num differs: " << pll_num << " " << other.pll_num << std::endl;
    }
    if (mash_order != other.mash_order) {
      std::cout << "mash_order differs: " << mash_order << " " << other.mash_order << std::endl;
    }
    if (mash_reset_n != other.mash_reset_n) {
      std::cout << "mash_reset_n differs: " << mash_reset_n << " " << other.mash_reset_n << std::endl;
    }
    if (outa_pd != other.outa_pd) {
      std::cout << "outa_pd differs: " << outa_pd << " " << other.outa_pd << std::endl;
    }
    if (outb_pd != other.outb_pd) {
      std::cout << "outb_pd differs: " << outb_pd << " " << other.outb_pd << std::endl;
    }
    if (outa_pwr != other.outa_pwr) {
      std::cout << "outa_pwr differs: " << outa_pwr << " " << other.outa_pwr << std::endl;
    }
    if (outb_pwr != other.outb_pwr) {
      std::cout << "outb_pwr differs: " << outb_pwr << " " << other.outb_pwr << std::endl;
    }
    if (out_iset != other.out_iset) {
      std::cout << "out_iset differs: " << out_iset << " " << other.out_iset << std::endl;
    }
    if (outa_mux != other.outa_mux) {
      std::cout << "outa_mux differs: " << outa_mux << " " << other.outa_mux << std::endl;
    }
    if (outb_mux != other.outb_mux) {
      std::cout << "outb_mux differs: " << outb_mux << " " << other.outb_mux << std::endl;
    }
    if (inpin_fmt != other.inpin_fmt) {
      std::cout << "inpin_fmt differs: " << inpin_fmt << " " << other.inpin_fmt << std::endl;
    }
    if (inpin_lvl != other.inpin_lvl) {
      std::cout << "inpin_lvl differs: " << inpin_lvl << " " << other.inpin_lvl << std::endl;
    }
    if (inpin_hyst != other.inpin_hyst) {
      std::cout << "inpin_hyst differs: " << inpin_hyst << " " << other.inpin_hyst << std::endl;
    }
    if (inpin_ignore != other.inpin_ignore) {
      std::cout << "inpin_ignore differs: " << inpin_ignore << " " << other.inpin_ignore << std::endl;
    }
    if (ld_type != other.ld_type) {
      std::cout << "ld_type differs: " << ld_type << " " << other.ld_type << std::endl;
    }
    if (ld_dly != other.ld_dly) {
      std::cout << "ld_dly differs: " << ld_dly << " " << other.ld_dly << std::endl;
    }
    if (mash_rst_count != other.mash_rst_count) {
      std::cout << "mash_rst_count differs: " << mash_rst_count << " " << other.mash_rst_count << std::endl;
    }
    if (sysref_repeat != other.sysref_repeat) {
      std::cout << "sysref_repeat differs: " << sysref_repeat << " " << other.sysref_repeat << std::endl;
    }
    if (sysref_en != other.sysref_en) {
      std::cout << "sysref_en differs: " << sysref_en << " " << other.sysref_en << std::endl;
    }
    if (sysref_pulse != other.sysref_pulse) {
      std::cout << "sysref_pulse differs: " << sysref_pulse << " " << other.sysref_pulse << std::endl;
    }
    if (sysref_div_pre != other.sysref_div_pre) {
      std::cout << "sysref_div_pre differs: " << sysref_div_pre << " " << other.sysref_div_pre << std::endl;
    }
    if (sysref_div != other.sysref_div) {
      std::cout << "sysref_div differs: " << sysref_div << " " << other.sysref_div << std::endl;
    }
    if (jesd_dac1_ctrl != other.jesd_dac1_ctrl) {
      std::cout << "jesd_dac1_ctrl differs: " << jesd_dac1_ctrl << " " << other.jesd_dac1_ctrl << std::endl;
    }
    if (jesd_dac2_ctrl != other.jesd_dac2_ctrl) {
      std::cout << "jesd_dac2_ctrl differs: " << jesd_dac2_ctrl << " " << other.jesd_dac2_ctrl << std::endl;
    }
    if (jesd_dac3_ctrl != other.jesd_dac3_ctrl) {
      std::cout << "jesd_dac3_ctrl differs: " << jesd_dac3_ctrl << " " << other.jesd_dac3_ctrl << std::endl;
    }
    if (jesd_dac4_ctrl != other.jesd_dac4_ctrl) {
      std::cout << "jesd_dac4_ctrl differs: " << jesd_dac4_ctrl << " " << other.jesd_dac4_ctrl << std::endl;
    }
    if (sysref_pulse_cnt != other.sysref_pulse_cnt) {
      std::cout << "sysref_pulse_cnt differs: " << sysref_pulse_cnt << " " << other.sysref_pulse_cnt << std::endl;
    }
    if (chdiv != other.chdiv) {
      std::cout << "chdiv differs: " << chdiv << " " << other.chdiv << std::endl;
    }
    if (vco_capctrl_strt != other.vco_capctrl_strt) {
      std::cout << "vco_capctrl_strt differs: " << vco_capctrl_strt << " " << other.vco_capctrl_strt << std::endl;
    }
    if (quick_recal_en != other.quick_recal_en) {
      std::cout << "quick_recal_en differs: " << quick_recal_en << " " << other.quick_recal_en << std::endl;
    }
    if (ramp_trig_cal != other.ramp_trig_cal) {
      std::cout << "ramp_trig_cal differs: " << ramp_trig_cal << " " << other.ramp_trig_cal << std::endl;
    }
    if (ramp_thresh != other.ramp_thresh) {
      std::cout << "ramp_thresh differs: " << ramp_thresh << " " << other.ramp_thresh << std::endl;
    }
    if (ramp_limit_high != other.ramp_limit_high) {
      std::cout << "ramp_limit_high differs: " << ramp_limit_high << " " << other.ramp_limit_high << std::endl;
    }
    if (ramp_limit_low != other.ramp_limit_low) {
      std::cout << "ramp_limit_low differs: " << ramp_limit_low << " " << other.ramp_limit_low << std::endl;
    }
    if (ramp_burst_count != other.ramp_burst_count) {
      std::cout << "ramp_burst_count differs: " << ramp_burst_count << " " << other.ramp_burst_count << std::endl;
    }
    if (ramp_burst_en != other.ramp_burst_en) {
      std::cout << "ramp_burst_en differs: " << ramp_burst_en << " " << other.ramp_burst_en << std::endl;
    }
    if (ramp_burst_trig != other.ramp_burst_trig) {
      std::cout << "ramp_burst_trig differs: " << ramp_burst_trig << " " << other.ramp_burst_trig << std::endl;
    }
    if (ramp_triga != other.ramp_triga) {
      std::cout << "ramp_triga differs: " << ramp_triga << " " << other.ramp_triga << std::endl;
    }
    if (ramp_trigb != other.ramp_trigb) {
      std::cout << "ramp_trigb differs: " << ramp_trigb << " " << other.ramp_trigb << std::endl;
    }
    if (ramp0_dly != other.ramp0_dly) {
      std::cout << "ramp0_dly differs: " << ramp0_dly << " " << other.ramp0_dly << std::endl;
    }
    if (ramp0_rst != other.ramp0_rst) {
      std::cout << "ramp0_rst differs: " << ramp0_rst << " " << other.ramp0_rst << std::endl;
    }
    if (ramp0_inc != other.ramp0_inc) {
      std::cout << "ramp0_inc differs: " << ramp0_inc << " " << other.ramp0_inc << std::endl;
    }
    if (ramp0_len != other.ramp0_len) {
      std::cout << "ramp0_len differs: " << ramp0_len << " " << other.ramp0_len << std::endl;
    }
    if (ramp0_next != other.ramp0_next) {
      std::cout << "ramp0_next differs: " << ramp0_next << " " << other.ramp0_next << std::endl;
    }
    if (ramp0_next_trig != other.ramp0_next_trig) {
      std::cout << "ramp0_next_trig differs: " << ramp0_next_trig << " " << other.ramp0_next_trig << std::endl;
    }
    if (ramp1_dly != other.ramp1_dly) {
      std::cout << "ramp1_dly differs: " << ramp1_dly << " " << other.ramp1_dly << std::endl;
    }
    if (ramp1_rst != other.ramp1_rst) {
      std::cout << "ramp1_rst differs: " << ramp1_rst << " " << other.ramp1_rst << std::endl;
    }
    if (ramp1_inc != other.ramp1_inc) {
      std::cout << "ramp1_inc differs: " << ramp1_inc << " " << other.ramp1_inc << std::endl;
    }
    if (ramp1_len != other.ramp1_len) {
      std::cout << "ramp1_len differs: " << ramp1_len << " " << other.ramp1_len << std::endl;
    }
    if (ramp1_next != other.ramp1_next) {
      std::cout << "ramp1_next differs: " << ramp1_next << " " << other.ramp1_next << std::endl;
    }
    if (ramp1_next_trig != other.ramp1_next_trig) {
      std::cout << "ramp1_next_trig differs: " << ramp1_next_trig << " " << other.ramp1_next_trig << std::endl;
    }
    if (ramp_dly_cnt != other.ramp_dly_cnt) {
      std::cout << "ramp_dly_cnt differs: " << ramp_dly_cnt << " " << other.ramp_dly_cnt << std::endl;
    }
    if (ramp_manual != other.ramp_manual) {
      std::cout << "ramp_manual differs: " << ramp_manual << " " << other.ramp_manual << std::endl;
    }
    if (ramp_scale_cnt != other.ramp_scale_cnt) {
      std::cout << "ramp_scale_cnt differs: " << ramp_scale_cnt << " " << other.ramp_scale_cnt << std::endl;
    }
    if (rb_vco_sel != other.rb_vco_sel) {
      std::cout << "rb_vco_sel differs: " << rb_vco_sel << " " << other.rb_vco_sel << std::endl;
    }
    if (rb_ld_vtune != other.rb_ld_vtune) {
      std::cout << "rb_ld_vtune differs: " << rb_ld_vtune << " " << other.rb_ld_vtune << std::endl;
    }
    if (rb_vco_capctrl != other.rb_vco_capctrl) {
      std::cout << "rb_vco_capctrl differs: " << rb_vco_capctrl << " " << other.rb_vco_capctrl << std::endl;
    }
    if (rb_vco_daciset != other.rb_vco_daciset) {
      std::cout << "rb_vco_daciset differs: " << rb_vco_daciset << " " << other.rb_vco_daciset << std::endl;
    }
  }
}
