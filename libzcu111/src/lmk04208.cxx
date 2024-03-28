#include <iostream>
#include <atomic>
#include <filesystem>
#include <initializer_list>
#include <vector>
#include <fmt/core.h>

extern "C" {
#include <i2c/smbus.h>
}

#include <piradio/clocks.hpp>

#include <unistd.h>

#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

namespace piradio
{
  class LMK04208
  {
    frequency fin0, fin1, foscin;
    
    int clkin0_div;
    int clkin1_div;
    
  public:
    LMK04208(const frequency &_fin0 = MHz(12.8),
	     const frequency &_fin1 = MHz(0),
	     const frequency &_foscin = MHz()) : fin0(_fin0), fin1(_fin1), foscin(_foscin)
    {
      
    }
  };
};
