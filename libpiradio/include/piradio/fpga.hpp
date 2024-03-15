#pragma once

#include <filesystem>

namespace piradio
{
  namespace fs = std::filesystem;
  
  class FPGA
  {
    fs::path configfs_path;

    const fs::path overlays_path() {
      return configfs_path / "device-tree/overlays";
    }
    
    const fs::path full_overlay_path() {
      return overlays_path() / "full";
    }
    
  public:
    FPGA();

    bool operating(void);

    bool overlay_loaded(void);
    bool remove_overlay(void);

    bool load_image(const std::filesystem::path &, const std::filesystem::path &);
  };
};
