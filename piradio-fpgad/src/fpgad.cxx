#include <iostream>
#include <map>
#include <cstring>
#include <cstdlib>
#include <thread>
#include <filesystem>

#include <systemd/sd-daemon.h>

#include <sdbus-c++/sdbus-c++.h>

#include <piradio/fpga.hpp>
#include <piradio/pidaemon.hpp>

#include <signal.h>

namespace fs = std::filesystem;

const std::string fpga_obj = "/io/piradio/fpgad/fpga";
const std::string fpga_iface = "io.piradio.fpgad.fpga";

fs::path fw_path = "/etc/piradio/firmware";

class FPGADaemon : public piradio::grpc_daemon
{
public:
  FPGADaemon() : grpc_daemon("io.piradio.fpgad") {
    std::cout << "FPGA operating: " << fpga.operating() << std::endl;

    create_sdbus_object(fpga_obj);

    register_sdbus_method(fpga_obj, fpga_iface, "reload_firmware", "", "", [this](sdbus::MethodCall c){ reload_firmware(c); });

    finalize_sdbus_object(fpga_obj);
  }

  void reload_firmware(sdbus::MethodCall call)
  {
    if (fpga.operating()) {
      fpga.remove_overlay();
    }

    fpga.load_image(fw_path / "bitstream", fw_path / "overlay");
    
    auto reply = call.createReply();
    reply.send();
  }
  
private:
  piradio::FPGA fpga;
};

void sighup(int signal) {
}

int main(int argc, char **argv)
{
  int result;
  
  FPGADaemon daemon;

  daemon.start();

  return daemon.wait_on();
}
