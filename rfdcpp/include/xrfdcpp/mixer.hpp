
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
    namespace mixer_mode {
      enum e {
	OFF = 0,
	C2C = 1,
	C2R = 2,
	R2C = 3,
	R2R = 4
      };
    };
    
    namespace mixer_type {
      enum e {
	OFF = 0,
	COARSE = 1,
	FINE = 2,
	DISABLED = 3
      };
    };
    
    namespace coarse_mixer {
      enum e {
	OFF = 0,
	F_2 = 2,
	F_4 = 4,
	FMIN_4 = 8,
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
    
    class Mixer
    {
    public:

      mixer_type::e type;
      mixer_mode::e mode;
      coarse_mixer::e coarse_freq;
      event_source::e evt_src;
      fine_mix_scale::e fine_scale;
      
      double freq;
      double phase_offset;
      
      bool validate(void) {
	if (!(phase_offset >= -180.0 && phase_offset <= 180.0)) {
	  return false;
	}
      }
    };
  };
};
