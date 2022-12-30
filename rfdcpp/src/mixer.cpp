#include <xrfdcpp/mixer.hpp>

namespace rfdc {
  namespace mixer {
    std::map<cmix_regs_t, cmix_cfg_t> cmix_map = {
      { { coarse_mix_regs::COARSE_MIX_BYPASS, coarse_mix_regs::COARSE_MIX_BYPASS, false }, { mixer_mode::C2C, coarse_mixer::BYPASS } },
      { { coarse_mix_regs::COARSE_MIX_BYPASS, coarse_mix_regs::COARSE_MIX_BYPASS, true }, { mixer_mode::C2C, coarse_mixer::BYPASS } },

      { { coarse_mix_regs::COARSE_MIX_BYPASS, coarse_mix_regs::COARSE_MIX_OFF, false }, { mixer_mode::R2R, coarse_mixer::BYPASS } },
      { { coarse_mix_regs::COARSE_MIX_BYPASS, coarse_mix_regs::COARSE_MIX_OFF, true }, { mixer_mode::R2R, coarse_mixer::BYPASS } },

      { { coarse_mix_regs::COARSE_MIX_OFF, coarse_mix_regs::COARSE_MIX_OFF, false }, { mixer_mode::C2C, coarse_mixer::OFF } },
      { { coarse_mix_regs::COARSE_MIX_OFF, coarse_mix_regs::COARSE_MIX_OFF, true }, { mixer_mode::C2C, coarse_mixer::OFF } },
      

      { { coarse_mix_regs::COARSE_MIX_4GSPS_ODD_FSBYTWO, coarse_mix_regs::COARSE_MIX_4GSPS_ODD_FSBYTWO, true }, { mixer_mode::C2C, coarse_mixer::F_2 } },
      { { coarse_mix_regs::COARSE_MIX_4GSPS_ODD_FSBYTWO, coarse_mix_regs::COARSE_MIX_OFF, true }, { mixer_mode::R2C, coarse_mixer::F_2 } },
      { { coarse_mix_regs::COARSE_MIX_I_ODD_FSBYFOUR, coarse_mix_regs::COARSE_MIX_Q_ODD_FSBYFOUR, true }, { mixer_mode::C2C, coarse_mixer::F_4 } },
      { { coarse_mix_regs::COARSE_MIX_Q_ODD_FSBYFOUR, coarse_mix_regs::COARSE_MIX_I_ODD_FSBYFOUR, true }, { mixer_mode::C2C, coarse_mixer::NEG_F_4 } },
      { { coarse_mix_regs::COARSE_MIX_OFF, coarse_mix_regs::COARSE_MIX_Q_ODD_FSBYFOUR, true }, { mixer_mode::R2C, coarse_mixer::F_4 } },
      { { coarse_mix_regs::COARSE_MIX_OFF, coarse_mix_regs::COARSE_MIX_I_ODD_FSBYFOUR, true }, { mixer_mode::R2C, coarse_mixer::NEG_F_4 } },

      { { coarse_mix_regs::COARSE_MIX_I_Q_FSBYTWO, coarse_mix_regs::COARSE_MIX_I_Q_FSBYTWO, false }, { mixer_mode::C2C, coarse_mixer::F_2 } },
      { { coarse_mix_regs::COARSE_MIX_I_Q_FSBYTWO, coarse_mix_regs::COARSE_MIX_OFF, false }, { mixer_mode::R2C, coarse_mixer::F_2 } },
      { { coarse_mix_regs::COARSE_MIX_I_FSBYFOUR, coarse_mix_regs::COARSE_MIX_Q_FSBYFOUR, false }, { mixer_mode::C2C, coarse_mixer::F_4 } },
      { { coarse_mix_regs::COARSE_MIX_R_I_FSBYFOUR, coarse_mix_regs::COARSE_MIX_R_Q_FSBYFOUR, false }, { mixer_mode::R2C, coarse_mixer::F_4 } },
      { { coarse_mix_regs::COARSE_MIX_Q_FSBYFOUR, coarse_mix_regs::COARSE_MIX_I_FSBYFOUR, false }, { mixer_mode::C2C, coarse_mixer::NEG_F_4 } },
      { { coarse_mix_regs::COARSE_MIX_R_I_MINFSBYFOUR, coarse_mix_regs::COARSE_MIX_R_Q_MINFSBYFOUR, false }, { mixer_mode::R2C, coarse_mixer::NEG_F_4 } },


      
    };

  }
};
