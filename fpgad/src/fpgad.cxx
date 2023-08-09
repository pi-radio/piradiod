#include <iostream>
#include <sstream>
#include <map>
#include <cstring>
#include <cstdlib>
#include <thread>
#include <filesystem>
#include <unordered_map>

#include <piradio/fpga.hpp>
#include <piradio/daemon.hpp>
#include <piradio/services.hpp>
#include <piradio/sdjournal.hpp>

#include <signal.h>

#include <mntent.h>

namespace fs = std::filesystem;

fs::path fw_path = "/etc/piradio/firmware";

int test_func(int a, int b)
{
  return 0;
}

class FPGADaemon : public piradio::grpc_daemon
{
public:
  FPGADaemon() : grpc_daemon(piradio::services::fpgad::bus) {
    std::cout << "FPGA operating: " << fpga.operating() << std::endl;

    if (!fs::exists("/configfs")) {
      fs::create_directory("/configfs");
    }

    
    auto obj = create_sdbus_object(piradio::services::fpgad::root_object);

    auto iface = create_sdbus_iface(obj, piradio::services::fpgad::root_interface);
    
    register_sdbus_method(iface, "reload_firmware", &FPGADaemon::reload_firmware);
    register_sdbus_signal(iface, "pre_remove_firmware", "");
    register_sdbus_signal(iface, "firmware_removed", "");
    
    finalize_sdbus_object(obj);

    if (!fpga.operating() && fs::exists(fw_path / "current")) {
      reload_firmware();
    }
  }

  void load_firmware(const std::string &name)
  {
    fs::path fw_dir = fw_path / name;
    
    if (!fs::exists(fw_dir)) {
      throw std::runtime_error("Firmware not found");
    }

    fs::path bitstream_path;
    fs::path overlay_path;
    
    for (const auto &entry : fs::directory_iterator(fw_dir)) {
      auto p = entry.path();
      
      if (p.extension() == ".bin") {
	if (!bitstream_path.empty()) {
	  throw std::runtime_error("Found multiple bitstreams");      
	}
	sdjournal::entry(sdjournal::info) << "Current firmware: " << p << std::endl;
	bitstream_path = p;
      }

      if (p.extension() == ".dtbo") {
	if (!overlay_path.empty()) {
	  throw std::runtime_error("Found multiple overlays");      
	}
	sdjournal::entry(sdjournal::info) << "Current overlay: " << p << std::endl;
	overlay_path = p;
      }
    }

    if (bitstream_path.empty()) {
      throw std::runtime_error("Current firmware has no bitstream");      
    }

    if(overlay_path.empty()) {
      throw std::runtime_error("Current firmware has no overlay");
    }

    fpga.load_image(bitstream_path, overlay_path);
    
  }
  
  void reload_firmware(void)
  {
    load_firmware("current");
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
