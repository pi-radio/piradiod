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
    
  protected:
    zcu111_i2c i2c;
  };
  
  class ZCU111
  {
  public:
    ZCU111();

    void mute_clocks(void);

    void tune_all(const frequency &freq);
    
    void program_lmx(int n);

    void i2c_program_lmx(uint8_t mask, const std::map<int, uint16_t> &regs);

  protected:
    Si5382 si5382;
    LMX2594 zcu111_lmx_A;
    LMX2594 zcu111_lmx_B;
    LMX2594 zcu111_lmx_C;
    zcu111_i2c i2c_spi;

    void write_i2c_spi(std::initializer_list<uint8_t> il);
  };
};
