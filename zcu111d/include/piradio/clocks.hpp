#pragma once

#include <vector>

#include <piradio/i2c.hpp>

namespace piradio
{
  void setup_clocks(void);
    
  void program_Si5382(zcu111_i2c &i2c, std::vector<std::tuple<uint8_t, uint8_t, uint8_t> > &regs);
  void program_LMX2594(zcu111_i2c &i2c, std::vector<unsigned int> &regs);
  void program_LMK04208(zcu111_i2c &i2c, std::vector<unsigned int> &regs);  
};
