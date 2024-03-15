#pragma once

#include <piradio/lmx2594.hpp>
#include <piradio/i2c.hpp>
#include <piradio/clocks.hpp>
#include <piradio/rfdc.hpp>

namespace piradio
{
  class Si5382
  {
  public:
    Si5382();

    void write_reg(uint8_t page, uint8_t reg, uint8_t val);    
  protected:
      
    zcu111_i2c i2c;
  };
  
  class ZCU111
  {
  public:    
    inline const static frequency default_reference = MHz(102.4);
    
    inline const static std::filesystem::path runtime_path = "/run/zcu111";
    
    inline const static std::filesystem::path si5382_path = runtime_path / "sfp_clk_programmed";
    
    inline const static std::filesystem::path ref_freq_path = runtime_path / "reference_frequency";
    
    inline const static std::filesystem::path LMX_A_path = runtime_path / "LMX" / "A";
    inline const static std::filesystem::path LMX_B_path = runtime_path / "LMX" / "B";
    inline const static std::filesystem::path LMX_C_path = runtime_path / "LMX" / "C";
    
    
    ZCU111();
    
    void enable_clocks(void);
    void mute_clocks(void);

    void tune_all(const frequency &freq);

    void tune_reference(const frequency &freq);

    void program_lmx(int n);
    void program_reference();
    void program_Si5382();
    
    void i2c_program_lmx(uint8_t mask, const std::map<int, uint16_t> &regs);

    void dump_lmx_regs(const frequency &freq);

    frequency get_reference_frequency() { return reference_frequency; }
    
  protected:
    frequency reference_frequency;
    
    Si5382 si5382;
    LMX2594 zcu111_lmx_A;
    LMX2594 zcu111_lmx_B;
    LMX2594 zcu111_lmx_C;
    zcu111_i2c i2c_spi;

    bool ref_programmed = false;

    void write_i2c_spi(std::initializer_list<uint8_t> il);

    void program_LMK04208(const std::vector<unsigned int> &regs);
  };
};
