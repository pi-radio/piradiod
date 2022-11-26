#include <iostream>
#include <filesystem>

#include <unistd.h>

#include <xrfdcpp/xrfdcpp.hpp>

int main(int argc, char **argv)
{
  XilinxRFDC rfdc;

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
  
  for (int i = 0; i < 4; i++) {
    XRFDCTile t = rfdc.adc(i);

    std::cout << "Tile " << i << std::endl;
    std::cout << " State: " << (t.state()) << std::endl;
    std::cout << " Status:" << (t.clock_detected() ? " CLOCK" : "")
	      << (t.supplies_up() ? " SUPPLIES" : "")
	      << (t.power_up() ? " POWER" : "")
	      << (t.pll_locked() ? " PLL" : "")
	      << std::endl;
    std::cout << " Clock Detector: " << (t.cdetect_status() ? "DETECTED" : "NOT DETECTED") << std::endl;
  }

  std::cout << std::endl;
  std::cout << "DACs:" << std::endl;
  
  for (int i = 0; i < 4; i++) {
    XRFDCTile t = rfdc.dac(i);

    std::cout << "Tile " << i << std::endl;
    std::cout << " State: " << (t.state()) << std::endl;
    std::cout << " Status:" << (t.clock_detected() ? " CLOCK" : "")
	      << (t.supplies_up() ? " SUPPLIES" : "")
	      << (t.power_up() ? " POWER" : "")
	      << (t.pll_locked() ? " PLL" : "")
	      << std::endl;
    std::cout << " Clock Detector: " << (t.cdetect_status() ? "DETECTED" : "NOT DETECTED") << std::endl;
  }
}
