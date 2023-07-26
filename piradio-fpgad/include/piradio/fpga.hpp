#pragma once

#include <filesystem>

namespace piradio
{
  class FPGA
  {
  public:
    FPGA();

    bool operating(void);

    bool overlay_loaded(void);
    bool remove_overlay(void);
    
    bool load_image(const std::filesystem::path &);
  };
};
