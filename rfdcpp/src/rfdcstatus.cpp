#include <iostream>
#include <filesystem>

#include <unistd.h>

#include <xrfdcpp/xrfdcpp.hpp>
#include <xrfdcpp/regs.hpp>

#include <magic_enum.hpp>

using namespace rfdc;

int main(int argc, char **argv)
{  
  RFDC rfdc;

  rfdc.reset();

  sleep(1);
  
  auto v = rfdc.version();

  std::cout << std::fixed;
  std::cout.precision(2);
  
  std::cout << "IP Version: "
	    << std::get<0>(v) << "."
	    << std::get<1>(v) << "."
	    << std::get<2>(v) << "."
	    << std::get<3>(v) << std::endl;

  std::cout << std::endl;
  std::cout << "ADCs:" << std::endl;

  int n_tile = 0;
  int n_adc = 0;
  
  for (auto &t: rfdc.get_adc_tiles()) {
    std::cout << "Tile " << n_tile << std::endl;
    std::cout << " State: " << (t.state()) << std::endl;
    std::cout << " Status:" << (t.clock_detected() ? " CLOCK" : "")
	      << (t.supplies_up() ? " SUPPLIES" : "")
	      << (t.power_up() ? " POWER" : "")
	      << (t.pll_locked() ? " PLL" : "")
	      << std::endl;
    std::cout << " Clock Detector: " << (t.cdetect_status() ? "DETECTED" : "NOT DETECTED") << std::endl;
    std::cout << " Clocks:" << std::endl;
    std::cout << "  Sample: " << t.sample_clock() << " Hz" << std::endl;
    std::cout << "  Reference: " << t.reference_clock() << " Hz (div: " << t.reference_div() << ")" << std::endl;
    std::cout << "  Fabric: " << t.fabric_clock() << " Hz" << std::endl;
    std::cout << "  Output: " << t.output_clock() << " Hz (div: " << t.output_div() << ")" << std::endl;
    
    int n_slice = 0;
    
    for (auto &adc: t.get_slices()) {
      std::cout << " ADC: " << n_adc << " (slice " << n_slice << ")" << std::endl;
      
      auto cmm = adc.mixer.get_coarse_mixer_mode();
      std::cout << "  Coarse Mixer: " << magic_enum::enum_name(std::get<0>(cmm)) << " " << magic_enum::enum_name(std::get<1>(cmm))  << std::endl;
      std::cout << "  Fine Mixer: " << magic_enum::enum_name(adc.mixer.get_fine_mixer_mode()) << std::endl;
      
      n_adc++;
      n_slice++;
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
