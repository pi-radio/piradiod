#pragma once

#include <vector>

#include <xrfdcpp/tile.hpp>
#include <xrfdcpp/slice.hpp>
#include <xrfdcpp/mixer.hpp>

namespace rfdc {

  /*
  class ADC : public ADCSlice
  {
  public:
    typedef std::shared_ptr<ADC> ptr_t;

    ADC(types::tile_t &, int, const types::acfg_t &, const types::dcfg_t &, types::csr_t);

    virtual bool is_adc(void) { return true; }
    virtual bool is_high_speed(void);

    virtual int get_calibration_mode(void);

    virtual nyquist_zone get_nyquist_zone(void);

  };
  */
  
  // class GEN3ADC


  class ADC : public Slice<ADCTile, cfg::adc_analog, cfg::adc_digital, csr::adc>
  {
  protected:
    nyquist_zone _get_nyquist_zone(void);
      
  public:
    static constexpr bool is_adc = true;
    
    typedef std::shared_ptr<ADC> ptr_t;
    
    ADC(ADCTile *_tile,
	int _n,
	const cfg::adc_analog &_acfg,
	const cfg::adc_digital &_dcfg,
	volatile csr::adc *_csr) : Slice(_tile,
				    _n,
				    _acfg,
				    _dcfg,
				    _csr)
    {
    }    
  };
  
  class LSADC : public ADC, public std::enable_shared_from_this<LSADC>
  {
  public:
    static constexpr int generation = 1;
    static constexpr bool high_speed = false;

    mixer::Mixer<LSADC, csr::adc> mixer;    
    
    LSADC(ADCTile *_tile,
	int _n,
	const cfg::adc_analog &_acfg,
	const cfg::adc_digital &_dcfg,
	volatile csr::adc *_csr) : ADC(_tile,
				    _n,
				    _acfg,
				    _dcfg,
				       _csr),
				   mixer(*this, _csr)
    {
    }

    virtual mixer::MixerBase *get_mixer(void) {
      return &mixer;
    }
    
    nyquist_zone get_nyquist_zone(void);

    virtual dfrequency_limits get_sampling_limits(void) {
      return dfrequency_limits(dfrequency::MHz(500), dfrequency::MHz(2058)); 
    }
  };

  class HSADC : public ADC, public std::enable_shared_from_this<HSADC>
  {
  public:
    static constexpr int generation = 1;
    static constexpr bool high_speed = true;

    mixer::Mixer<HSADC, csr::adc> mixer0;    
    mixer::Mixer<HSADC, csr::adc> mixer1;    

    virtual mixer::MixerBase *get_mixer(void) {
      return &mixer1;
    }

    
    HSADC(ADCTile *_tile,
	  int _n,
	  const cfg::adc_analog &_acfg,
	  const cfg::adc_digital &_dcfg,
	  volatile csr::adc *_csr0,
	  volatile csr::adc *_csr1) : ADC(_tile,
					  _n,
					  _acfg,
					  _dcfg,
					  _csr1),
				      mixer0(*this, _csr0),
				      mixer1(*this, _csr1)
    {
    }

    nyquist_zone get_nyquist_zone(void);
    
    virtual int get_calibration_mode(void);
    virtual dfrequency_limits get_sampling_limits(void) {
      return dfrequency_limits(dfrequency::MHz(1000), dfrequency::MHz(4116));
    }
  };
  
  class ADCTile : public Tile<cfg::adc, csr::adc_tile>, public std::enable_shared_from_this<ADCTile>
  {    
    std::vector<ADC::ptr_t> slices;

  public:
    typedef volatile csr::adc_tile csr_t;
    
    ADCTile(const tile_params<cfg::adc, csr::adc_tile> &p);
    
    std::vector<ADC::ptr_t> &get_slices(void) {
      return slices;
    }
    
    ADC::ptr_t get_adc(int n) {
      return slices[n];
    }

    bool is_enabled(void);
    
    uint32_t get_path_enabled_reg(void);
  };
};  
