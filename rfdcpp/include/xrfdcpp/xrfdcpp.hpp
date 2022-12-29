#pragma once

#include <vector>

#include <xrfdcpp/adc.hpp>
#include <xrfdcpp/dac.hpp>

namespace rfdc {
  class RFDC
  {
    volatile struct csr::rfdc *csr;
    uint64_t csr_len;
    int uio_fd;

    cfg::dc config;
  
    int generation;

    int n_dac_tiles;
    int n_dac_slices;

    int n_adc_tiles;
    int n_adc_slices;

    std::vector<ADCTile> adc_tiles;
    std::vector<DACTile> dac_tiles;  

    std::vector<std::reference_wrapper<ADC> > adcs;
    std::vector<std::reference_wrapper<DAC> > dacs;
  
  public:
    RFDC();
    ~RFDC();

    std::tuple<int, int, int, int> version();

    void reset();
  
    uint32_t POSM();

    auto &get_adcs(void) {
      return adcs;
    }
  
    auto &get_dacs(void) {
      return dacs;
    }
  
    auto &get_adc_tiles(void) {
      return adc_tiles;
    }

    auto &get_dac_tiles(void) {
      return dac_tiles;
    }
    
    ADCTile &get_adc_tile(int n) {
      return adc_tiles[n];
    }
  
    DACTile &get_dac_tile(int n) {
      return dac_tiles[n];
    }

    int get_n_adc_tiles(void) {
      return n_adc_tiles;
    }

    int get_n_dac_tiles(void) {
      return n_dac_tiles;
    }
  
    int get_n_adc_slices(void) {
      return n_adc_slices;
    }

    int get_n_dac_slices(void) {
      return n_dac_slices;
    }
  };
};
