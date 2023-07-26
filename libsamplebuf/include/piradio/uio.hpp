#pragma once

#include <map>
#include <filesystem>
#include <string>
#include <cmath>
#include <stdint.h>

namespace piradio
{
  class uio_map
  {
    uint32_t _map_no;
    uint64_t _addr;
    uint64_t _offset;
    uint64_t _size;
    int fd;

    void *_buffer;

    std::filesystem::path dir_entry;
    
  public:
    uio_map(const std::filesystem::path &map_entry_path, int dev_fd);
    ~uio_map();
    
    uint32_t map_no(void) { return _map_no; }
    uint64_t addr(void) { return _addr; }
    uint64_t offset(void) { return _offset; }
    uint64_t size(void) { return _size; }

    template <class T> T *buffer(void) { return reinterpret_cast<T*>(_buffer); }
  };

  class uio_device
  {
    int fd;
    std::filesystem::path sysfs_path;
    std::map<int, uio_map *> maps;
    
  public:
    uio_device(const std::filesystem::path &_sysfs_path);

    std::string get_uio_name();

    int n_maps(void) { return maps.size(); }
    uio_map *get_map(int n) { return maps[n]; }
  };
};
