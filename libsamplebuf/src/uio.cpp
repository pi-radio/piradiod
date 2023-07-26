#include <string>
#include <cstring>
#include <iostream>
#include <fstream>
#include <filesystem>
#include <chrono>
#include <thread>
#include <cassert>

#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>

#include <arpa/inet.h>

#include <fmt/core.h>

#include <piradio/uio.hpp>

namespace piradio
{
  static const std::filesystem::path uio_class_root{"/sys/class/uio"};
  static const std::filesystem::path dev_root{"/dev"};

  uio_map::uio_map(const std::filesystem::path &map_entry_path, int dev_fd) : dir_entry(map_entry_path), fd(dev_fd)
  {
      std::string addr_s, offset_s, size_s;
      auto filename = dir_entry.filename().string();

      assert(filename.starts_with("map"));

      filename.erase(0,3);

      _map_no = std::stoul(filename);
      
      std::ifstream(dir_entry / "addr") >> addr_s;
      std::ifstream(dir_entry / "offset") >> offset_s;
      std::ifstream(dir_entry / "size") >> size_s;
      
      _addr = std::stoul(addr_s, nullptr, 16);
      _offset = std::stoul(offset_s, nullptr, 16);
      _size = std::stoul(size_s, nullptr, 16);
      
      _buffer = mmap(NULL, _size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, _map_no * getpagesize());

      if (_buffer == MAP_FAILED) {
	std::cerr << std::strerror(errno) << std::endl;
	throw std::runtime_error("Unable to map region");
      }
  }

  uio_map::~uio_map()
  {
    if (_buffer != nullptr) munmap(_buffer, _size);
  }

  uio_device::uio_device(const std::filesystem::path &_sysfs_path) : sysfs_path(_sysfs_path), fd(-1)
  {
    std::string uio_name = get_uio_name();
    
    if (uio_name.empty()) {
      std::ofstream driver_override(sysfs_path / "driver_override");
      
      driver_override << "uio_pdrv_genirq" << std::endl;

      std::this_thread::sleep_for(std::chrono::milliseconds(100));

      uio_name = get_uio_name();

      if (uio_name.empty()) {
	throw std::runtime_error("Unable to attach uio driver");
      }
    }

    const char *dev_path_cs = (dev_root / uio_name).c_str();
    
    fd = open(dev_path_cs, O_RDWR | O_SYNC | O_NONBLOCK);

    if (fd == -1) {
      throw std::runtime_error(fmt::format("Unable to open {}: {}", dev_path_cs, std::strerror(errno)));
    }
    
    auto maps_path = uio_class_root / uio_name / "maps";

    for (auto const &dir_entry : std::filesystem::directory_iterator(maps_path)) {
      uio_map *map = new uio_map(dir_entry, fd);
      
      assert(map->map_no() < 2);

      maps[map->map_no()] = map;
    }
  }

  std::string uio_device::get_uio_name()
  {
    std::string uio_name;
    
    for (auto const &uio_entry : std::filesystem::directory_iterator(sysfs_path / "uio")) {
      if (!uio_name.empty()) {
	throw std::runtime_error("Found multiple uio entries");
      }

      uio_name = uio_entry.path().filename().string();
    }

    return uio_name;
  }
};
