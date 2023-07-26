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

#include <piradio/trigger.hpp>

namespace piradio
{
  std::filesystem::path trigger::get_sysfs_path(void)
  {
   const std::filesystem::path devices_path{"/sys/bus/platform/devices"};
   const std::string suffix(".piradip_trigger_unit");
   
   for (auto const &dir_entry : std::filesystem::directory_iterator(devices_path)) {
     auto fn = dir_entry.path().filename();
     
     if (fn.string().ends_with(suffix)) {
       return dir_entry.path();
     }
    }
   
   throw std::runtime_error("Unable to find trigger unit");
  }
  
  trigger::trigger() : uio_device(get_sysfs_path())
  {
    assert(n_maps() == 1);
    
    csr = get_map(0)->buffer<trigger_csr>();

    assert(csr->ip_id == 0x50545247);
  }
};
