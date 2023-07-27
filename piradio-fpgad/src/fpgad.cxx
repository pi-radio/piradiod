#include <iostream>
#include <map>
#include <cstring>
#include <cstdlib>
#include <thread>

#include <systemd/sd-daemon.h>

#include <sdbus-c++/sdbus-c++.h>

#include <piradio/fpga.hpp>

#include <signal.h>

const std::string dbus_service_name = "io.pi-rad.fpgad";
const std::string dbus_service_object = "/io/pi-rad/fpgad/service";
const std::string dbus_fpga_object = "/io/pi-rad/fpgad/fpga";

class FPGADaemon
{
public:
  FPGADaemon() {
    fpga = new piradio::FPGA();

    std::cout << "FPGA operating: " << fpga->operating() << std::endl;
  }

  int run() {
    sd_notify(0, "READY=1");
    while(true);
  }
  
private:
  piradio::FPGA *fpga;  
};

void sighup(int signal) {
}

int main(int argc, char **argv)
{
  int result;
  
  
  auto connection = sdbus::createSystemBusConnection(dbus_service_name);

  auto service_control = sdbus::createObject(*connection, dbus_service_object);
  auto fpga_control = sdbus::createObject(*connection, dbus_fpga_object);

  FPGADaemon daemon;

  std::thread daemon_thread([&daemon]() { daemon.run(); });

  while (true) {
    int recv_sig;
    sigset_t sset;
    
    result = sigwait(&sset, &recv_sig);

    if (result != 0) {
      std::cerr << "sigwait failed: " << std::strerror(result) << std::endl;
    }

    std::cout << "Signal: " << recv_sig << std::endl;

    if (recv_sig == SIGTERM || recv_sig == SIGINT) {
      std::exit(0);
    }
  }


  return 0;
}
