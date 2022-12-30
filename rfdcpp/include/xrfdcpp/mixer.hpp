#pragma once

#include <iostream>
#include <map>

#include <xrfdcpp/bitfield.hpp>

namespace rfdc {
  namespace event_source {
    enum e {
      IMMEDIATE = 0,
      SLICE = 1,
      TILE = 2,
      SYSREF = 3,
      MARKER = 4,
      PL = 5
    };
  };
  
  namespace mixer {
    enum class mixer_mode {
      OFF = 0,
      C2C = 1,
      C2R = 2,
      R2C = 3,
      R2R = 4
    };
    
    enum class mixer_type {
      OFF = 0,
      COARSE = 1,
      FINE = 2,
      DISABLED = 3
    };
    
    namespace coarse_mixer {
      enum e {
	OFF = 0,
	F_2 = 2,
	F_4 = 4,
	NEG_F_4 = 8,
	BYPASS = 16
      };
    };
    
    namespace coarse_mix_mode {
      enum e {
	C2C_C2R = 1,
	R2C = 2
      };
    };

    namespace fine_mix_scale {
      enum e {
	AUTO = 0,
	S_1P0 = 1,
	S_0P7 = 2
      };
    }

    namespace coarse_mix_regs {
      const uint32_t COARSE_MIX_OFF    = 0x924;
      const uint32_t COARSE_MIX_BYPASS = 0x000;

      const uint32_t COARSE_MIX_4GSPS_ODD_FSBYTWO = 0x492;
      
      const uint32_t COARSE_MIX_I_ODD_FSBYFOUR = 0x2CB;
      const uint32_t COARSE_MIX_Q_ODD_FSBYFOUR = 0x659;

      const uint32_t COARSE_MIX_I_Q_FSBYTWO = 0x410;

      const uint32_t COARSE_MIX_I_FSBYFOUR = 0x298;
      const uint32_t COARSE_MIX_Q_FSBYFOUR = 0x688;

      const uint32_t COARSE_MIX_I_MINFSBYFOUR = 0x688;
      const uint32_t COARSE_MIX_Q_MINFSBYFOUR = 0x298;

      const uint32_t COARSE_MIX_R_I_FSBYFOUR = 0x8A0;
      const uint32_t COARSE_MIX_R_Q_FSBYFOUR = 0x70C;

      const uint32_t COARSE_MIX_R_I_MINFSBYFOUR = 0x8A0;
      const uint32_t COARSE_MIX_R_Q_MINFSBYFOUR = 0x31C;
    }
    
    typedef std::tuple<uint32_t, uint32_t, bool> cmix_regs_t;
    typedef std::tuple<mixer_mode, coarse_mixer::e> cmix_cfg_t;
    
    extern std::map<cmix_regs_t, cmix_cfg_t> cmix_map;
    
    
    template <class slice> class Mixer
    {
      slice::csr_t *mix_csr;


      
    public:      
      
      mixer_type type;
      mixer_mode mode;
      coarse_mixer::e coarse_freq;
      event_source::e evt_src;
      fine_mix_scale::e fine_scale;

      slice &s;
      
      double freq;
      double phase_offset;
      
      bool validate(void) {
	if (!(phase_offset >= -180.0 && phase_offset <= 180.0)) {
	  return false;
	}
      }

      Mixer(slice &_slice, slice::csr_t *_csr) : s(_slice), mix_csr(_csr) {
      }

      
      
      cmix_cfg_t get_coarse_mixer_mode(void) {
	uint32_t c0 = mix_csr->mxr_cfg0;
	uint32_t c1 = mix_csr->mxr_cfg1;
	
	cmix_regs_t r(c0, c1, s.is_high_speed());

	return cmix_map[r];
      }

      mixer_mode get_fine_mixer_mode(void) {
	static bitfield<uint32_t> i_mode_bf(0, 2);

	uint32_t fmm = mix_csr->mxr_mode;
	
	auto i_mode = bitfield(0,2).get(fmm);
	auto q_mode = bitfield(2,2).get(fmm);

	if (i_mode == 0x3 && q_mode == 0x3) {
	  return mixer_mode::C2C;
	} else if (i_mode == 0x3 && q_mode == 0x0) {
	  return mixer_mode::C2R;
	} else if (i_mode == 0x1 && q_mode == 0x1) {
	  return mixer_mode::R2C;
	} else {
	  return mixer_mode::OFF;
	}
      }

      mixer_mode get_mixer_mode(void) {
	auto fmm = get_fine_mixer_mode(); 

	if (fmm != mixer_mode::OFF) {
	  return fmm;
	}

	auto t = get_coarse_mixer_mode();

	return std::get<0>(t);
      }

      uint32_t get_raw_phase_offset(void) {
	return (bitfield(0,2).get(mix_csr->nco_phase_upp) << 16) |
	  bitfield(0,16).get(mix_csr->nco_phase_low);
      }

      double get_phase_offset_deg(void) {
	return double(get_raw_phase_offset()) * 180.0 / (1 << 17);
      }

      uint64_t get_raw_nco_frequency(void) {
	return (uint64_t(bitfield(0, 16).get(mix_csr->nco_fqwd_upp)) << 32) |
	  (bitfield(0,16).get(mix_csr->nco_fqwd_mid) << 16) |
	  bitfield(0,16).get(mix_csr->nco_fqwd_low);
      }

      double get_nco_frequency_hz(void) {
	return double(get_raw_nco_frequency()) * s.get_sampling_freq_hz() / (1ULL << 48);
      }
      
      
      
      bool is_coarse_mixer(void) {
	auto fmm = get_fine_mixer_mode(); 
	auto t = get_coarse_mixer_mode();

	return fmm == mixer_mode::OFF && std::get<0>(t) != mixer_mode::OFF;
      }
      
    };
  };
};
