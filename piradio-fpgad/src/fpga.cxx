#include <piradio/fpga.hpp>

#include <filesystem>
#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>

namespace fs = std::filesystem;

const fs::path manager_path = "/sys/class/fpga_manager";
const fs::path fpga0_path = manager_path / "fpga0";

const fs::path configfs_path = "/configfs";
const fs::path overlays_path = configfs_path / "device-tree/overlays";
const fs::path full_overlay_path = overlays_path / "full";

namespace piradio
{
  FPGA::FPGA()
  {
    if (!fs::exists(manager_path)) {
      throw std::runtime_error("FPGA manager not found");
    }
    
    if (!fs::exists(fpga0_path)) {
      throw std::runtime_error("FPGA 0 not found");
    }

    if (!fs::exists(configfs_path)) {
      fs::create_directory(configfs_path);
      std::string command = std::string("mount -t configfs configfs ") + configfs_path.string();
      std::system(command.c_str());
    }    
  }
  
  bool FPGA::operating(void)
  {
    std::ifstream state_file(fpga0_path / "state");
    std::stringstream s;

    s << state_file.rdbuf();

    std::cout << s.str() << std::endl;
    
    return (s.str() == "operating\n");
  }

  bool FPGA::overlay_loaded(void)
  {
    return fs::exists(full_overlay_path) && fs::is_directory(full_overlay_path);
  }

  bool FPGA::remove_overlay(void)
  {
    return fs::remove(full_overlay_path);
  }
  
  bool load_image(const std::filesystem::path &image_path, const std::filesystem::path &overlay_path)
  {
    
  }
};
