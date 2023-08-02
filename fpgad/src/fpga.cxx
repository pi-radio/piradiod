#include <piradio/fpga.hpp>

#include <filesystem>
#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <chrono>

namespace fs = std::filesystem;

const fs::path manager_path = "/sys/class/fpga_manager";
const fs::path fpga0_path = manager_path / "fpga0";

const fs::path configfs_path = "/configfs";
const fs::path overlays_path = configfs_path / "device-tree/overlays";
const fs::path full_overlay_path = overlays_path / "full";

const fs::path firmware_dest_dir = "/lib/firmware";

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
  
  bool FPGA::load_image(const std::filesystem::path &image_path, const std::filesystem::path &overlay_path)
  {
    bool retval = false;
    
    if (operating()) {
      remove_overlay();
    }

    fs::path firmware_dest = firmware_dest_dir / image_path.filename();
    fs::path overlay_dest = firmware_dest_dir / overlay_path.filename();
    
    if (!fs::exists("/lib/firmware")) {
      fs::create_directory("/lib/firmware");
    }

    fs::copy_file(image_path, firmware_dest);
    fs::copy_file(overlay_path, overlay_dest);

    auto start = std::chrono::high_resolution_clock::now();

    fs::create_directory(full_overlay_path);

    {
      std::ofstream flag_stream(fpga0_path / "flags");

      flag_stream << "0" << std::endl;
    }
    
    {
      std::ofstream ovl_stream(full_overlay_path / "path");

      ovl_stream << overlay_path.filename().c_str();

      ovl_stream.flush();
    }

    {
      std::ifstream ovl_stream(full_overlay_path / "path");
      std::stringstream s;

      s << ovl_stream.rdbuf();

      std::string rs = s.str();

      rs.erase(rs.end()-1);
      
      if (rs == overlay_path.filename()) {
	retval = true;
      } else {
	std::cout << "Overlay load failed: " << s.str() << std::endl;
      }
    }

    if (retval) retval = operating();
          
    auto stop = std::chrono::high_resolution_clock::now();

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);

    std::cout << "FW prog elapsed time: " << duration.count() << "ms" << std::endl;

    if (!retval) {
      std::cout << "FW prog failed" << std::endl;
    }
    
    fs::remove(firmware_dest);
    fs::remove(overlay_dest);

    
    return retval;
  }
};
