#pragma once

#include <filesystem>

namespace piradio
{
  namespace fs = std::filesystem;

  class zcu111_i2c
  {
    int fd;
    fs::path dev_path;
    
  public:
    static int find_device(uint8_t addr);
    
    zcu111_i2c(int n, uint8_t addr);

    int read(void);
    uint8_t read(uint8_t cmd);
    int read(uint8_t cmd, uint8_t *len, uint8_t *buf);
    int write(uint8_t cmd);
    int write(uint8_t addr, uint8_t byte);
    int write(uint8_t cmd, std::initializer_list<uint8_t> il);
  };  
};
