#pragma once

#include <cmath>
#include <iomanip>

#include <piradio/rfdc_tile.hpp>
#include <piradio/rfdc_str.hpp>

namespace piradio
{

  template <class tile_type>
  class RFDCBlock
  {
  public:
    RFDCBlock(tile_type &_tile, int _block) : tile(_tile),
					      block(_block),
					      id_string(_tile.get_id_string() + " " + std::to_string(block))
    {
    }

    bool enabled() const
    {
      return tile.enabled();
    }
    
    template <class C, class F>
    int _compare_field(const C &a, const C &b, F C::*ptr, const std::string &name)
    {
      if (a.*ptr != b.*ptr) {
	std::cout << name << " differs: " << a.*ptr << " " << b.*ptr << std::endl;
	return -1;
      }

      return 0;
    }

    void display_mixer_settings(const XRFdc_Mixer_Settings &a)
    {
      std::cout << std::setw(32) << a.Freq << std::endl;
      
      std::cout << "Freq: " << a.Freq << std::endl;
      std::cout << "Phase Offset: " << a.PhaseOffset << std::endl;
      std::cout << "Event Source: " << a.EventSource << std::endl;
      std::cout << "Coarse Mix Freq: " << a.CoarseMixFreq << std::endl;
      std::cout << "Mixer Mode: " << rfdc::str::mixer_modes[a.MixerMode] << std::endl;
      std::cout << "Fine Mixer Scale: " << a.FineMixerScale << std::endl;
      std::cout << "Mixer Type: " << rfdc::str::mixer_types[a.MixerType] << std::endl;
    }
    
    
    int compare_mixer_settings(const XRFdc_Mixer_Settings &a, const XRFdc_Mixer_Settings &b)
    {
      int retval = 0;

      if (std::fabs(a.Freq - b.Freq) > 1.0) {
	std::cout << "Freq differs" << std::endl;
	retval = -1;
      }
      
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::PhaseOffset, "Phase Offset") ? -1 : retval;
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::EventSource, "Event Source") ? -1 : retval;
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::CoarseMixFreq, "Coarse Mix Freq") ? -1 : retval;
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::MixerMode, "Mixer Mode") ? -1 : retval;
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::FineMixerScale, "Fine Mixer Scale") ? -1 : retval;
      retval = _compare_field(a, b, &XRFdc_Mixer_Settings::MixerType, "Mixer Type") ? -1 : retval;

      if (retval) {
	std::cout << "A:" << std::endl;
	display_mixer_settings(a);
	std::cout << "B:" << std::endl;
	display_mixer_settings(b);
      }
      
      return retval;
    }
      
    XRFdc_Mixer_Settings get_mixer_settings(void)
    {
      int result;
      XRFdc_Mixer_Settings settings;

      result = rfdc_func(XRFdc_GetMixerSettings, &settings);

      if (result != XRFDC_SUCCESS) {
	throw std::runtime_error("Unable to get mixer settings");
      }

      return settings;
    }

    void set_mixer_settings(const XRFdc_Mixer_Settings &settings, bool verify=false)
    {
      int result;

      result = rfdc_func(XRFdc_SetMixerSettings, (XRFdc_Mixer_Settings *)&settings);

      if (result != XRFDC_SUCCESS) {
	throw std::runtime_error("Unable to set mixer settings");
      }

      if (verify) {
	assert(!compare_mixer_settings(settings, get_mixer_settings()));
      }
    }

    frequency sample_freq(void) {
      return tile.sample_freq();
    }
    
    frequency ref_clk_freq(void) {
      return tile.ref_clk_freq();
    }    

    void bypass_mixer()
    {
      XRFdc_Mixer_Settings s;

      s.Freq = 0;
      s.PhaseOffset = 0;
      s.EventSource = XRFDC_EVNT_SRC_TILE;
      s.CoarseMixFreq = XRFDC_COARSE_MIX_BYPASS;
      s.MixerMode = XRFDC_MIXER_MODE_R2R;

      s.FineMixerScale = XRFDC_MIXER_SCALE_1P0;
      s.MixerType = XRFDC_MIXER_TYPE_COARSE;
    
      set_mixer_settings(s, true);
    }
    
    void disable_NCO()
    {
      XRFdc_Mixer_Settings s;

      s.Freq = 0;
      s.PhaseOffset = 0;
      s.EventSource = XRFDC_EVNT_SRC_TILE;
      s.CoarseMixFreq = XRFDC_COARSE_MIX_BYPASS;
      s.MixerMode = XRFDC_MIXER_MODE_R2R;

      s.FineMixerScale = XRFDC_MIXER_SCALE_1P0;
      s.MixerType = XRFDC_MIXER_TYPE_COARSE;
    
      set_mixer_settings(s, true);
    }

    piradio::frequency NCO_freq(void) {
      return piradio::MHz(get_mixer_settings().Freq);
    }

    void tune_NCO(piradio::frequency f, double phase = 0.0)
    {
      tune_NCO(f.Hz(), phase);
    }

    void set_coarse(unsigned v)
    {
      XRFdc_Mixer_Settings s;

      s.Freq = 0;
      s.PhaseOffset = 0;
      s.EventSource = XRFDC_EVNT_SRC_TILE;
      s.CoarseMixFreq = v;

      if (std::is_same<tile_type, ADCTile>::value)
	s.MixerMode = XRFDC_MIXER_MODE_R2C;
      else if (std::is_same<tile_type, DACTile>::value)
	s.MixerMode = XRFDC_MIXER_MODE_C2R;
      else
	throw std::runtime_error("Invalid tile type");
      
      s.FineMixerScale = XRFDC_MIXER_SCALE_1P0;
      s.MixerType = XRFDC_MIXER_TYPE_COARSE;
    
      set_mixer_settings(s, true);
      
      tile.update_tile(XRFDC_EVENT_MIXER);
    }
    
    void set_fs2()
    {
      set_coarse(XRFDC_COARSE_MIX_SAMPLE_FREQ_BY_TWO);
    }

    void set_fs4()
    {
      set_coarse(XRFDC_COARSE_MIX_SAMPLE_FREQ_BY_FOUR);
    }
    
    void set_neg_fs4()
    {
      set_coarse(XRFDC_COARSE_MIX_MIN_SAMPLE_FREQ_BY_FOUR);
    }
    
    void tune_NCO(double freq, double phase = 0.0)
    {
      XRFdc_Mixer_Settings s;

      s.Freq = freq / 1e6;
      s.PhaseOffset = phase;
      s.EventSource = XRFDC_EVNT_SRC_TILE;
      s.CoarseMixFreq = XRFDC_COARSE_MIX_OFF;

      if (std::is_same<tile_type, ADCTile>::value)
	s.MixerMode = XRFDC_MIXER_MODE_R2C;
      else if (std::is_same<tile_type, DACTile>::value)
	s.MixerMode = XRFDC_MIXER_MODE_C2R;
      else
	throw std::runtime_error("Invalid tile type");
      
      s.FineMixerScale = XRFDC_MIXER_SCALE_1P0;
      s.MixerType = XRFDC_MIXER_TYPE_FINE;
    
      set_mixer_settings(s, true);
      
      rfdc_func(XRFdc_ResetNCOPhase);
      
      tile.update_tile(XRFDC_EVENT_MIXER);
    }

    XRFdc_BlockStatus block_status(void) {
      XRFdc_BlockStatus retval;

      rfdc_func(XRFdc_GetBlockStatus, &retval);

      return retval;
    }

    inline u32 reg_offset() { return XRFDC_BLOCK_ADDR_OFFSET(block); }

    inline u64 read64(u32 addr) { return tile.read_drp64(reg_offset() + addr); }
    inline u32 read32(u32 addr) { return tile.read_drp32(reg_offset() + addr); }
    inline u16 read16(u32 addr) { return tile.read_drp16(reg_offset() + addr); }
    inline u8 read8(u32 addr) { return tile.read_drp8(reg_offset() + addr); }

    inline void write64(u32 addr, u64 v) { tile.write_drp64(reg_offset() + addr, v); }
    inline void write32(u32 addr, u32 v) { tile.write_drp32(reg_offset() + addr, v); }
    inline void write16(u32 addr, u16 v) { tile.write_drp16(reg_offset() + addr, v); }
    inline void write8(u32 addr, u8 v) { tile.write_drp8(reg_offset() + addr, v); }
    
  protected:
    tile_type &tile;
    int block;

    const std::string id_string;
  
    template <typename F, class... types> int rfdc_tile_func(F f, types... args)
    {
      return tile.rfdc_func(f, args...);
    }
  
    template <typename F, class... types> int rfdc_func(F f, types... args)
    {
      return tile.rfdc_func(f, block, args...);
    }

    template <typename F, class... types> int rfdc_func_no_type(F f, types... args)
    {
      return tile.rfdc_func_no_type(f, block, args...);
    }

  };


  class ADC : public RFDCBlock<ADCTile>
  {
  public:
    ADC(ADCTile &_tile, int _block);

    void set_mixer_passthrough(void);

    void set_attenuation(bool, float);
    
    void dump(void);

    uint32_t decimation_factor(void) {
      u32 df;

      rfdc_func_no_type(XRFdc_GetDecimationFactor, &df);

      return df;
    }
    
  private:
  
  
  };

  class DAC : public RFDCBlock<DACTile>
  {
  public:
    DAC(DACTile &_tile, int _block);

    int get_inv_sinc_mode() {
      u16 mode;
      
      rfdc_func_no_type(XRFdc_GetInvSincFIR, &mode);

      return mode;
    }

    void set_inv_sinc_mode(int mode) {
      std::cout << "Setting mode to " << mode << std::endl;
      rfdc_func_no_type(XRFdc_SetInvSincFIR, mode);
    }
    
  private:
  
  };

#if 0
typedef struct {
	u32 BlockAvailable;
	u32 InvSyncEnable;
	u32 MixMode;
	u32 DecoderMode;
} XRFdc_DACBlock_AnalogDataPath_Config;

/**
 * DAC block Digital DataPath Config settings.
 */
typedef struct {
	u32 MixerInputDataType;
	u32 DataWidth;
	u32 InterpolationMode;
	u32 FifoEnable;
	u32 AdderEnable;
	u32 MixerType;
} XRFdc_DACBlock_DigitalDataPath_Config;

/**
 * ADC block Analog DataPath Config settings.
 */
typedef struct {
	u32 BlockAvailable;
	u32 MixMode;
} XRFdc_ADCBlock_AnalogDataPath_Config;

/**
 * DAC block Digital DataPath Config settings.
 */
typedef struct {
	u32 MixerInputDataType;
	u32 DataWidth;
	u32 DecimationMode;
	u32 FifoEnable;
	u32 MixerType;
} XRFdc_ADCBlock_DigitalDataPath_Config;

/**
 * DAC Tile Config structure.
 */
typedef struct {
	u32 Enable;
	u32 PLLEnable;
	double SamplingRate;
	double RefClkFreq;
	double FabClkFreq;
	u32 FeedbackDiv;
	u32 OutputDiv;
	u32 RefClkDiv;
	u32 MultibandConfig;
	double MaxSampleRate;
	u32 NumSlices;
	u32 LinkCoupling;
	XRFdc_DACBlock_AnalogDataPath_Config DACBlock_Analog_Config[4];
	XRFdc_DACBlock_DigitalDataPath_Config DACBlock_Digital_Config[4];
} XRFdc_DACTile_Config;

/**
 * ADC Tile Config Structure.
 */
typedef struct {
	u32 Enable; /* Tile Enable status */
	u32 PLLEnable; /* PLL enable Status */
	double SamplingRate;
	double RefClkFreq;
	double FabClkFreq;
	u32 FeedbackDiv;
	u32 OutputDiv;
	u32 RefClkDiv;
	u32 MultibandConfig;
	double MaxSampleRate;
	u32 NumSlices;
	XRFdc_ADCBlock_AnalogDataPath_Config ADCBlock_Analog_Config[4];
	XRFdc_ADCBlock_DigitalDataPath_Config ADCBlock_Digital_Config[4];
} XRFdc_ADCTile_Config;

/**
 * RFdc Config Structure.
 */
typedef struct {
	u32 DeviceId;
	metal_phys_addr_t BaseAddr;
	u32 ADCType; /* ADC Type 4GSPS or 2GSPS*/
	u32 MasterADCTile; /* ADC master Tile */
	u32 MasterDACTile; /* DAC Master Tile */
	u32 ADCSysRefSource;
	u32 DACSysRefSource;
	u32 IPType;
	u32 SiRevision;
	XRFdc_DACTile_Config DACTile_Config[4];
	XRFdc_ADCTile_Config ADCTile_Config[4];
} XRFdc_Config;

/**
 * DAC Block Analog DataPath Structure.
 */
typedef struct {
	u32 Enabled; /* DAC Analog Data Path Enable */
	u32 MixedMode;
	double TerminationVoltage;
	double OutputCurrent;
	u32 InverseSincFilterEnable;
	u32 DecoderMode;
	void *FuncHandler;
	u32 NyquistZone;
	u8 AnalogPathEnabled;
	u8 AnalogPathAvailable;
	XRFdc_QMC_Settings QMC_Settings;
	XRFdc_CoarseDelay_Settings CoarseDelay_Settings;
} XRFdc_DACBlock_AnalogDataPath;

/**
 * DAC Block Digital DataPath Structure.
 */
typedef struct {
	u32 MixerInputDataType;
	u32 DataWidth;
	int ConnectedIData;
	int ConnectedQData;
	u32 InterpolationFactor;
	u8 DigitalPathEnabled;
	u8 DigitalPathAvailable;
	XRFdc_Mixer_Settings Mixer_Settings;
} XRFdc_DACBlock_DigitalDataPath;

/**
 * ADC Block Analog DataPath Structure.
 */
typedef struct {
	u32 Enabled; /* ADC Analog Data Path Enable */
	XRFdc_QMC_Settings QMC_Settings;
	XRFdc_CoarseDelay_Settings CoarseDelay_Settings;
	XRFdc_Threshold_Settings Threshold_Settings;
	u32 NyquistZone;
	u8 CalibrationMode;
	u8 AnalogPathEnabled;
	u8 AnalogPathAvailable;
} XRFdc_ADCBlock_AnalogDataPath;

/**
 * ADC Block Digital DataPath Structure.
 */
typedef struct {
	u32 MixerInputDataType;
	u32 DataWidth;
	u32 DecimationFactor;
	int ConnectedIData;
	int ConnectedQData;
	u8 DigitalPathEnabled;
	u8 DigitalPathAvailable;
	XRFdc_Mixer_Settings Mixer_Settings;
} XRFdc_ADCBlock_DigitalDataPath;

/**
 * DAC Tile Structure.
 */
typedef struct {
	u32 TileBaseAddr; /* Tile  BaseAddress*/
	u32 NumOfDACBlocks; /* Number of DAC block enabled */
	XRFdc_PLL_Settings PLL_Settings;
	u8 MultibandConfig;
	XRFdc_DACBlock_AnalogDataPath DACBlock_Analog_Datapath[4];
	XRFdc_DACBlock_DigitalDataPath DACBlock_Digital_Datapath[4];
} XRFdc_DAC_Tile;

/**
 * ADC Tile Structure.
 */
typedef struct {
	u32 TileBaseAddr;
	u32 NumOfADCBlocks; /* Number of ADC block enabled */
	XRFdc_PLL_Settings PLL_Settings;
	u8 MultibandConfig;
	XRFdc_ADCBlock_AnalogDataPath ADCBlock_Analog_Datapath[4];
	XRFdc_ADCBlock_DigitalDataPath ADCBlock_Digital_Datapath[4];
} XRFdc_ADC_Tile;

/**
 * RFdc Structure.
 */
typedef struct {
	XRFdc_Config RFdc_Config; /* Config Structure */
	u32 IsReady;
	u32 ADC4GSPS;
	metal_phys_addr_t BaseAddr; /* BaseAddress */
	struct metal_io_region *io; /* Libmetal IO structure */
	struct metal_device *device; /* Libmetal device structure */
	XRFdc_DAC_Tile DAC_Tile[4];
	XRFdc_ADC_Tile ADC_Tile[4];
	XRFdc_StatusHandler StatusHandler; /* Event handler function */
	void *CallBackRef; /* Callback reference for event handler */
	u8 UpdateMixerScale; /* Set to 1, if user overwrite mixer scale */
} XRFdc;

  
#endif
  
};
