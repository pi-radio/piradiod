#pragma once

#include <vector>
#include <map>

#include <piradio/i2c.hpp>

namespace piradio
{
  void program_Si5382(zcu111_i2c &i2c, const std::vector<std::tuple<uint8_t, uint8_t, uint8_t> > &regs);
  void program_LMX2594(zcu111_i2c &i2c, const std::map<int, uint16_t> &regs);
  void program_LMK04208(zcu111_i2c &i2c, const std::vector<unsigned int> &regs);  

  extern const std::map<int, uint16_t> LMX4GHz_template;
  extern const std::vector<unsigned int> LMK04208_regs;
  extern const std::vector<unsigned int> LMX_regs_4GHz;
  extern const std::vector<std::tuple<uint8_t, uint8_t, uint8_t> > si_122_88;
};
