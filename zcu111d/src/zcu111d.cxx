#include <iostream>
#include <map>

#include <systemd/sd-daemon.h>

#include <sdbus-c++/sdbus-c++.h>

#include <piradio/clocks.hpp>

int main(int argc, char **argv)
{
  piradio::setup_clocks();
	       
  return 0;
}
