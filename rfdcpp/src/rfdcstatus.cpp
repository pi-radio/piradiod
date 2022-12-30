#include <iostream>
#include <filesystem>

#include <unistd.h>

#include <xrfdcpp/xrfdcpp.hpp>
#include <xrfdcpp/regs.hpp>

using namespace rfdc;

int main(int argc, char **argv)
{  
  RFDC rfdc;

  rfdc.reset();

  sleep(1);
  
  auto v = rfdc.version();
  
  std::cout << "IP Version: "
	    << std::get<0>(v) << "."
	    << std::get<1>(v) << "."
	    << std::get<2>(v) << "."
	    << std::get<3>(v) << std::endl;

  std::cout << std::endl;
  std::cout << "ADCs:" << std::endl;

  int n_tile = 0;
  
  for (auto &t: rfdc.get_adc_tiles()) {
    std::cout << "Tile " << n_tile << std::endl;
    std::cout << " State: " << (t.state()) << std::endl;
    std::cout << " Status:" << (t.clock_detected() ? " CLOCK" : "")
	      << (t.supplies_up() ? " SUPPLIES" : "")
	      << (t.power_up() ? " POWER" : "")
	      << (t.pll_locked() ? " PLL" : "")
	      << std::endl;
    std::cout << " Clock Detector: " << (t.cdetect_status() ? "DETECTED" : "NOT DETECTED") << std::endl;

    for (auto &adc: t.get_slices()) {
      auto cmm = adc.mixer.get_coarse_mixer_mode();
      std::cout << std::get<0>(cmm) << " " << std::get<1>(cmm)  << std::endl;
    }
    
    n_tile++;
  }

  std::cout << std::endl;
  std::cout << "DACs:" << std::endl;

  n_tile = 0;
  
  for (auto &t: rfdc.get_dac_tiles()) {
    std::cout << "Tile " << n_tile << std::endl;
    std::cout << " State: " << (t.state()) << std::endl;
    std::cout << " Status:" << (t.clock_detected() ? " CLOCK" : "")
	      << (t.supplies_up() ? " SUPPLIES" : "")
	      << (t.power_up() ? " POWER" : "")
	      << (t.pll_locked() ? " PLL" : "")
	      << std::endl;
    std::cout << " Clock Detector: " << (t.cdetect_status() ? "DETECTED" : "NOT DETECTED") << std::endl;
    n_tile++;
  }
}
