#pragma once

#include <vector>
#include <memory>

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

    std::vector<std::shared_ptr<ADCTile>> adc_tiles;
    std::vector<std::shared_ptr<DACTile>> dac_tiles;  

    std::vector<std::shared_ptr<ADC>> adcs;
    std::vector<std::shared_ptr<DAC>> dacs;
  
  public:
    RFDC();
    ~RFDC();

    std::tuple<int, int, int, int> version();

    void reset();
  
    uint32_t POSM();

    uint32_t get_tiles_enabled_mask(void) {
      return csr->tiles_enabled;
    }

    uint32_t get_adc_paths_enabled(void) {
      return csr->adc_paths_enabled;
    }
    
    uint32_t get_dac_paths_enabled(void) {
      return csr->dac_paths_enabled;
    }

    int get_generation(void) {
      return generation;
    }
    
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
      return *adc_tiles[n];
    }
  
    DACTile &get_dac_tile(int n) {
      return *dac_tiles[n];
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
