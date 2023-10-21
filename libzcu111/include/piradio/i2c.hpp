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
    static int find_LMXs();
    
    zcu111_i2c(int n, uint8_t addr);

    int read(void);
    uint8_t read(uint8_t cmd);
    int read(uint8_t cmd, uint8_t *buf);
    void write(uint8_t cmd, int retries=10);
    void write(uint8_t addr, uint8_t byte, int retries=10);
    void write(uint8_t cmd, std::initializer_list<uint8_t> il, int retries=10);
    void write(std::initializer_list<uint8_t> il, int retries=10);

    void txn(uint16_t addr, std::initializer_list<uint8_t> il, int retries=10);
  };  
};
