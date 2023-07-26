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

#include <piradio/samplebuf.hpp>

namespace piradio
{
  static const std::filesystem::path uio_class_root{"/sys/class/uio"};
  static const std::filesystem::path dev_root{"/dev"};

  std::filesystem::path sample_buffer::get_sysfs_path(int _dir, int _n)
  {
    std::filesystem::path _sysfs_path;
    
    const std::filesystem::path devices_path{"/sys/bus/platform/devices"};

    std::string dir_s((_dir == IN) ? "in" : "out");
    std::string suffix = std::string(".axis_sample_buffer_") + dir_s;
    
    for (auto const &dir_entry : std::filesystem::directory_iterator(devices_path)) {
      auto fn = dir_entry.path().filename();

      if (!fn.string().ends_with(suffix)) {
	continue;
      }

      auto p = dir_entry.path() / "of_node" / "sample-buffer-no";

      std::ifstream f(p);

      int np;
      
      f.read((char *)&np, 4);

      np = ntohl(np);

      if (np == _n) {
	_sysfs_path = dir_entry.path();
	break;
      }
    }
    
    if (_sysfs_path.empty()) {
      throw std::runtime_error(std::string("Unable to find sample buffer ") + dir_s + " " + std::to_string(n));
    }

    return _sysfs_path;
  }
  
  sample_buffer::sample_buffer(direction_e _direction, int _n) : direction(_direction), n(_n),
								 uio_device(get_sysfs_path(_direction, _n))
  {
    assert(n_maps() == 2);
    
    csr = get_map(0)->buffer<sample_buffer_csr>();
    
    if (csr->ip_id != 0x5053424F) {
      throw std::runtime_error("Found invalid IP id");
    }
  }
}
