#include <iostream>
#include <sstream>
#include <map>
#include <cstring>
#include <cstdlib>
#include <thread>
#include <filesystem>
#include <unordered_map>
#include <cassert>

#include <grpc/grpc.h>
#include <grpcpp/security/server_credentials.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>

#include <piradio/fpga.hpp>
#include <piradio/daemon.hpp>
#include <piradio/services.hpp>
#include <piradio/sdjournal.hpp>
#include <piradio/zcu111.hpp>
#include <piradio/rfdc_manager.hpp>

#include <signal.h>

#include <mntent.h>

namespace fs = std::filesystem;
using namespace piradio;

fs::path fw_path = "/etc/piradio/firmware";
fs::path run_path = "/run/fpgad";

class FPGADaemon : public grpc_daemon
{
public:
  FPGADaemon() : grpc_daemon(services::fpgad::bus) {
    fs::create_directory(run_path, "/run");
    
    std::cout << "FPGA operating: " << fpga.operating() << std::endl;


    
    auto obj = create_sdbus_object(services::fpgad::root_object);

    auto iface = create_sdbus_iface(obj, services::fpgad::root_interface);
    
    register_sdbus_method(iface, "reload_firmware", &FPGADaemon::reload_firmware);
    register_sdbus_signal(iface, "pre_remove_firmware", "");
    register_sdbus_signal(iface, "firmware_removed", "");
    
    finalize_sdbus_object(obj);

    if (fpga.operating()) {
      rfdc.attach_rfdc();

      zcu111.tune_clocks(rfdc.rfdc(), false);
    } else if (fs::exists(fw_path / "current")) {
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

    rfdc.shutdown_rfdc();

    zcu111.mute_clocks();

    fpga.load_image(bitstream_path, overlay_path);

    try {
      rfdc.attach_rfdc();

      zcu111.tune_clocks(rfdc.rfdc());

      rfdc.startup_rfdc();      
    } catch(...) {
    }
  }
  
  void reload_firmware(void)
  {
    load_firmware("current");
  }
    
private:
  FPGA fpga;

  RFDCManager rfdc;
  ZCU111Manager zcu111;
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
