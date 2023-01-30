
def bitfield(v, s, l):
    return ((v >> s) & ((1 << l) - 1))
        

class LMXRegs:
    def __init__(self, config):
        self.LMX = config
        
    def get_reg(self, rno):
        if not isinstance(rno, int):
            raise Exception(f"Invalid register number {rno}")
        if rno == 112:
            return (0x0000 | (bitfield(self.LMX.rb_vco_daciset, 0, 9) << 0))
        if rno == 111:
            return (0x0000 | (bitfield(self.LMX.rb_vco_capctrl, 0, 8) << 0))
        if rno == 110:
            return (0x0000 | (bitfield(self.LMX.rb_vco_sel, 0, 3) << 5) | (bitfield(self.LMX.rb_ld_vtune, 0, 2) << 9))
        if rno == 109:
            return 0x0000
        if rno == 108:
            return 0x0000
        if rno == 107:
            return 0x0000
        if rno == 106:
            return (0x0000 | (bitfield(self.LMX.ramp_trig_cal, 0, 1) << 4) | (bitfield(self.LMX.ramp_scale_cnt, 0, 3) << 0))
        if rno == 105:
            return (0x0000 | (bitfield(self.LMX.ramp1_next, 0, 1) << 4) | (bitfield(self.LMX.ramp1_next_trig, 0, 2) << 0) | (bitfield(self.LMX.ramp_dly_cnt, 0, 10) << 6) | (bitfield(self.LMX.ramp_manual, 0, 1) << 5))
        if rno == 104:
            return (0x0000 | (bitfield(self.LMX.ramp1_len, 0, 16) << 0))
        if rno == 103:
            return (0x0000 | (bitfield(self.LMX.ramp1_inc, 0, 16) << 0))
        if rno == 102:
            return (0x0000 | (bitfield(self.LMX.ramp1_inc, 16, 14) << 0))
        if rno == 101:
            return (0x0000 | (bitfield(self.LMX.ramp0_next, 0, 1) << 4) | (bitfield(self.LMX.ramp0_next_trig, 0, 2) << 0) | (bitfield(self.LMX.ramp1_dly, 0, 1) << 6) | (bitfield(self.LMX.ramp1_rst, 0, 1) << 5))
        if rno == 100:
            return (0x0000 | (bitfield(self.LMX.ramp0_len, 0, 16) << 0))
        if rno == 99:
            return (0x0000 | (bitfield(self.LMX.ramp0_inc, 0, 16) << 0))
        if rno == 98:
            return (0x0000 | (bitfield(self.LMX.ramp0_dly, 0, 1) << 0) | (bitfield(self.LMX.ramp0_inc, 16, 14) << 2))
        if rno == 97:
            return (0x0800 | (bitfield(self.LMX.ramp_burst_trig, 0, 2) << 0) | (bitfield(self.LMX.ramp_triga, 0, 4) << 3) | (bitfield(self.LMX.ramp_trigb, 0, 4) << 7) | (bitfield(self.LMX.ramp0_rst, 0, 1) << 15))
        if rno == 96:
            return (0x0000 | (bitfield(self.LMX.ramp_burst_count, 0, 13) << 2) | (bitfield(self.LMX.ramp_burst_en, 0, 1) << 15))
        if rno == 95:
            return 0x0000
        if rno == 94:
            return 0x0000
        if rno == 93:
            return 0x0000
        if rno == 92:
            return 0x0000
        if rno == 91:
            return 0x0000
        if rno == 90:
            return 0x0000
        if rno == 89:
            return 0x0000
        if rno == 88:
            return 0x0000
        if rno == 87:
            return 0x0000
        if rno == 86:
            return (0x0000 | (bitfield(self.LMX.ramp_limit_low, 0, 16) << 0))
        if rno == 85:
            return (0x0000 | (bitfield(self.LMX.ramp_limit_low, 16, 16) << 0))
        if rno == 84:
            return (0x0000 | (((self.LMX.ramp_limit_low >> 32) & 1) << 0))
        if rno == 83:
            return (0x0000 | (bitfield(self.LMX.ramp_limit_high, 0, 16) << 0))
        if rno == 82:
            return (0x0000 | (bitfield(self.LMX.ramp_limit_high, 16, 16) << 0))
        if rno == 81:
            return (0x0000 | (((self.LMX.ramp_limit_high >> 32) & 1) << 0))
        if rno == 80:
            return (0x0000 | (bitfield(self.LMX.ramp_thresh, 0, 16) << 0))
        if rno == 79:
            return (0x0000 | (bitfield(self.LMX.ramp_thresh, 16, 16) << 0))
        if rno == 78:
            return (0x0001 | (bitfield(self.LMX.vco_capctrl_strt, 0, 8) << 1) | (bitfield(self.LMX.quick_recal_en, 0, 1) << 9) | (((self.LMX.ramp_thresh >> 32) & 1) << 11))
        if rno == 77:
            return 0x0000
        if rno == 76:
            return 0x000c
        if rno == 75:
            return (0x0800 | (bitfield(self.LMX.chdiv, 0, 5) << 6))
        if rno == 74:
            return (0x0000 | (bitfield(self.LMX.jesd_dac3_ctrl, 0, 6) << 0) | (bitfield(self.LMX.jesd_dac4_ctrl, 0, 6) << 6) | (bitfield(self.LMX.sysref_pulse_cnt, 0, 4) << 12))
        if rno == 73:
            return (0x0000 | (bitfield(self.LMX.jesd_dac1_ctrl, 0, 6) << 0) | (bitfield(self.LMX.jesd_dac2_ctrl, 0, 6) << 6))
        if rno == 72:
            return (0x0000 | (bitfield(self.LMX.sysref_div, 0, 11) << 0))
        if rno == 71:
            return (0x0001 | (bitfield(self.LMX.sysref_repeat, 0, 1) << 2) | (bitfield(self.LMX.sysref_en, 0, 1) << 3) | (bitfield(self.LMX.sysref_pulse, 0, 1) << 4) | (bitfield(self.LMX.sysref_div_pre, 0, 3) << 5))
        if rno == 70:
            return (0x0000 | (bitfield(self.LMX.mash_rst_count, 0, 16) << 0))
        if rno == 69:
            return (0x0000 | (bitfield(self.LMX.mash_rst_count, 16, 16) << 0))
        if rno == 68:
            return 0x03e8
        if rno == 67:
            return 0x0000
        if rno == 66:
            return 0x01f4
        if rno == 65:
            return 0x0000
        if rno == 64:
            return 0x1388
        if rno == 63:
            return 0x0000
        if rno == 62:
            return 0x0322
        if rno == 61:
            return 0x00a8
        if rno == 60:
            return (0x0000 | (bitfield(self.LMX.ld_dly, 0, 16) << 0))
        if rno == 59:
            return (0x0000 | (bitfield(self.LMX.ld_type, 0, 1) << 0))
        if rno == 58:
            return (0x0001 | (bitfield(self.LMX.inpin_fmt, 0, 3) << 9) | (bitfield(self.LMX.inpin_lvl, 0, 2) << 12) | (bitfield(self.LMX.inpin_hyst, 0, 1) << 14) | (bitfield(self.LMX.inpin_ignore, 0, 1) << 15))
        if rno == 57:
            return 0x0020
        if rno == 56:
            return 0x0000
        if rno == 55:
            return 0x0000
        if rno == 54:
            return 0x0000
        if rno == 53:
            return 0x0000
        if rno == 52:
            return 0x0820
        if rno == 51:
            return 0x0080
        if rno == 50:
            return 0x0000
        if rno == 49:
            return 0x4180
        if rno == 48:
            return 0x0300
        if rno == 47:
            return 0x0300
        if rno == 46:
            return (0x07fc | (bitfield(self.LMX.outb_mux, 0, 2) << 0))
        if rno == 45:
            return (0xc0c0 | (bitfield(self.LMX.outb_pwr, 0, 6) << 0) | (bitfield(self.LMX.out_iset, 0, 2) << 9) | (bitfield(self.LMX.outa_mux, 0, 2) << 11))
        if rno == 44:
            return (0x0000 | (bitfield(self.LMX.mash_order, 0, 3) << 0) | (bitfield(self.LMX.mash_reset_n, 0, 1) << 5) | (bitfield(self.LMX.outa_pd, 0, 1) << 6) | (bitfield(self.LMX.outb_pd, 0, 1) << 7) | (bitfield(self.LMX.outa_pwr, 0, 6) << 8))
        if rno == 43:
            return (0x0000 | (bitfield(self.LMX.pll_num, 0, 16) << 0))
        if rno == 42:
            return (0x0000 | (bitfield(self.LMX.pll_num, 16, 16) << 0))
        if rno == 41:
            return (0x0000 | (bitfield(self.LMX.mash_seed, 0, 16) << 0))
        if rno == 40:
            return (0x0000 | (bitfield(self.LMX.mash_seed, 16, 16) << 0))
        if rno == 39:
            return (0x0000 | (bitfield(self.LMX.pll_den, 0, 16) << 0))
        if rno == 38:
            return (0x0000 | (bitfield(self.LMX.pll_den, 16, 16) << 0))
        if rno == 37:
            return (0x0004 | (bitfield(self.LMX.pfd_dly_sel, 0, 6) << 8) | (bitfield(self.LMX.mash_seed_en, 0, 1) << 15))
        if rno == 36:
            return (0x0000 | (bitfield(self.LMX.pll_n, 0, 16) << 0))
        if rno == 35:
            return 0x0004
        if rno == 34:
            return (0x0000 | (bitfield(self.LMX.pll_n, 16, 3) << 0))
        if rno == 33:
            return 0x1e21
        if rno == 32:
            return 0x0393
        if rno == 31:
            return (0x03ec | (bitfield(self.LMX.seg1_en, 0, 1) << 14))
        if rno == 30:
            return 0x318c
        if rno == 29:
            return 0x318c
        if rno == 28:
            return 0x0488
        if rno == 27:
            return (0x0002 | (bitfield(self.LMX.vco2x_en, 0, 1) << 0))
        if rno == 26:
            return 0x0db0
        if rno == 25:
            return 0x0c2b
        if rno == 24:
            return 0x071a
        if rno == 23:
            return 0x007c
        if rno == 22:
            return 0x0001
        if rno == 21:
            return 0x0401
        if rno == 20:
            return (0xc048 | (bitfield(self.LMX.vco_sel_force, 0, 1) << 10) | (bitfield(self.LMX.vco_sel, 0, 3) << 11))
        if rno == 19:
            return (0x2700 | (bitfield(self.LMX.vco_capctrl, 0, 8) << 0))
        if rno == 18:
            return 0x0064
        if rno == 17:
            return (0x0000 | (bitfield(self.LMX.vco_daciset_strt, 0, 9) << 0))
        if rno == 16:
            return (0x0000 | (bitfield(self.LMX.vco_daciset, 0, 9) << 0))
        if rno == 15:
            return 0x064f
        if rno == 14:
            return (0x1e00 | (bitfield(self.LMX.cpg, 0, 3) << 4))
        if rno == 13:
            return 0x4000
        if rno == 12:
            return (0x5000 | (bitfield(self.LMX.pll_r_pre, 0, 8) << 0))
        if rno == 11:
            return (0x0008 | (bitfield(self.LMX.pll_r, 0, 8) << 4))
        if rno == 10:
            return (0x1058 | (bitfield(self.LMX.mult, 0, 5) << 7))
        if rno == 9:
            return (0x0604 | (bitfield(self.LMX.osc_2x, 0, 1) << 12))
        if rno == 8:
            return (0x2000 | (bitfield(self.LMX.vco_capctrl_force, 0, 1) << 11) | (bitfield(self.LMX.vco_daciset_force, 0, 1) << 14))
        if rno == 7:
            return (0x00b2 | (bitfield(self.LMX.out_force, 0, 1) << 14))
        if rno == 6:
            return 0xc802
        if rno == 5:
            return 0x00c8
        if rno == 4:
            return 0x0a43
        if rno == 3:
            return 0x0642
        if rno == 2:
            return 0x0500
        if rno == 1:
            return (0x0808 | (bitfield(self.LMX.cal_clk_div, 0, 3) << 0))
        if rno == 0:
            return (0x2410 | (bitfield(self.LMX.powerdown, 0, 1) << 0) | (bitfield(self.LMX.reset, 0, 1) << 1) | (bitfield(self.LMX.muxout_ld_sel, 0, 1) << 2) | (bitfield(self.LMX.fcal_en, 0, 1) << 3) | (bitfield(self.LMX.fcal_lpfd_adj, 0, 2) << 5) | (bitfield(self.LMX.fcal_hpfd_adj, 0, 2) << 7) | (bitfield(self.LMX.out_mute, 0, 1) << 9) | (bitfield(self.LMX.vco_phase_sync, 0, 1) << 14) | (bitfield(self.LMX.ramp_en, 0, 1) << 15))


        
        raise Exception(f"Undefined register {rno}")
                        
    def __getitem__(self, items):
        try:
            return [ self.get_reg(rno) for rno in items ]
        except TypeError:
            return self.get_reg(items)
