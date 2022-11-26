#include <iostream>
#include <fstream>
#include <string>

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>


#include <pirsamp/pirsamp.hpp>

#include <pybind11/pybind11.h>

namespace fs = std::filesystem;

template< typename T >
std::string addr_to_hex( T i, int n = sizeof(T)*2 )
{
  std::stringstream stream;
  stream << std::setfill ('0') << std::setw(n) 
         << std::hex << i;
  return stream.str();
}

PiRadioUIOMap::~PiRadioUIOMap()
{
  if (base != NULL) {
    munmap((void *)base, len);
  }  
}

PiRadioUIO::PiRadioUIO(const std::filesystem::path &p)
{
  int page_size = getpagesize();
  
  if (!fs::exists(p)) {
    throw std::runtime_error(p.string() + " not found.");
  }

  std::string uio_name;
  
  for (auto const &dir_entry : fs::directory_iterator{p / "uio"}) {
    if (dir_entry.path().filename().string().find("uio") == 0) {
      uio_name = dir_entry.path().filename();
    } else {
      std::cerr << "Unknown entry in uio dir: " << dir_entry << std::endl;
    }
  }

  if (uio_name.length() == 0) {
    throw std::runtime_error(std::string("Could not find uio for device ") + p.string());
  }

  uio_fd = open((fs::path("/dev") / uio_name).c_str(), O_RDWR);

  if (uio_fd < 0) {
    throw std::runtime_error("Could not open UIO device");
  }

  fs::path uio_dir = fs::path("/sys/class/uio") / uio_name;

  for (auto const &de : fs::directory_iterator(uio_dir / "maps")) {
    auto map_dir = de.path();
    std::string s = map_dir.filename().string();

    if (!s.starts_with("map")) {
      throw std::runtime_error(std::string("Unexpected file ") + s + " in maps directory");
    }

    s.erase(0, 3);
    
    int i = std::stol(s);

    std::ifstream addr_f(map_dir / "addr");
    std::ifstream offset_f(map_dir / "offset");
    std::ifstream size_f(map_dir / "size");

    uint64_t addr;
    uint64_t offset;
    uint64_t size;

    addr_f >> std::hex >> addr;
    offset_f >> std::hex >> offset;
    size_f >> std::hex >> size;
    
    volatile void *p = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, uio_fd, i * page_size);

    if (p != MAP_FAILED) {
      maps.emplace(i, std::forward_as_tuple(p, size));
    } else {
      throw std::runtime_error("Map failed");
    }
  }
}

PiRadioUIO::~PiRadioUIO()
{
  close(uio_fd);
}

struct PiRadioSampleBufferCSR {
  uint32_t id;
  uint32_t ctrl_stat;
  uint32_t start;
  uint32_t end;
  uint32_t stream_depth;
  uint32_t dummy;
} __attribute__((packed));


PiRadioSampleBuffer::PiRadioSampleBuffer(const fs::path &p) :
  PiRadioUIO(p)
{
  csr = get_map_base<PiRadioSampleBufferCSR>(0);
}

volatile uint32_t *PiRadioSampleBuffer::get_buffer_addr()
{
  return get_map_base<uint32_t>(1);
}

ssize_t PiRadioSampleBuffer::get_size()
{
  return get_map_len(1);
}

PiRadioSampleBufferIn::PiRadioSampleBufferIn(uint64_t base) :
  PiRadioSampleBuffer(fs::path("/sys/devices/platform/axi") /
		      (addr_to_hex(base, 8) + ".axis_sample_buffer_in"))
{
}

PiRadioSampleBufferOut::PiRadioSampleBufferOut(uint64_t base) :
  PiRadioSampleBuffer(fs::path("/sys/devices/platform/axi") /
		      (addr_to_hex(base, 8) + ".axis_sample_buffer_out"))
{
}


struct PiRadioTriggerCSR {
  uint32_t id;
  uint32_t trigger_mask;
  uint32_t trigger;
  uint32_t delay[32];
} __attribute__((packed));



PiRadioTrigger::PiRadioTrigger(uint64_t base) :
  PiRadioUIO(fs::path("/sys/devices/platform/axi") /
	     (addr_to_hex(base, 8) + ".piradip_trigger_unit"))
{
  csr = get_map_base<PiRadioTriggerCSR>(0);
}

void PiRadioTrigger::trigger(void)
{
  csr->trigger = 1;
}


static const std::string sbo_prefix("axis_sample_buffer_out@");
static const std::string sbi_prefix("axis_sample_buffer_in@");
static const std::string ptu_prefix("piradip_trigger_unit@");

PiRadioSampleBuffers::PiRadioSampleBuffers()
{
  trigger_addr = 0;
  
  fs::path dev_path("/sys/firmware/devicetree/base/axi");
  
  for (auto const &dir_entry : fs::directory_iterator{dev_path}) {
    std::string s = dir_entry.path().filename().string(); 
    if (s.starts_with(sbo_prefix)) {
      s.erase(0, sbo_prefix.length());
      
      uint64_t addr = std::stol(s, nullptr, 16);
      
      auto p = dir_entry.path() / "piradio-dac";
      
      int n;
      std::ifstream fs(p);
      fs >> n;
      
      DAC_obj.emplace(n, std::make_shared<PiRadioSampleBufferOut>(addr));
    } else if (s.starts_with(sbi_prefix)) {
      s.erase(0, sbi_prefix.length());
      
      uint64_t addr = std::stol(s, nullptr, 16);
      
      auto p = dir_entry.path() / "piradio-adc";
      
      int n;
      std::ifstream fs(p);
      fs >> n;
      
      ADC_obj.emplace(n, std::make_shared<PiRadioSampleBufferIn>(addr));
    } else if (s.starts_with(ptu_prefix)) {
      s.erase(0, ptu_prefix.length());
      
      triggers.emplace(0, std::make_shared<PiRadioTrigger>(std::stol(s, nullptr, 16)));
    }
  }
}

PiRadioSampleBufferIn::ptr PiRadioSampleBuffers::get_adc(int n)
{
  return ADC_obj[n];
}

PiRadioSampleBufferOut::ptr PiRadioSampleBuffers::get_dac(int n)
{
  return DAC_obj[n];
}

PiRadioTrigger::ptr PiRadioSampleBuffers::get_trigger()
{
  return triggers[0];
}

PiRadioSampleBuffers sample_buffers;

int add(int a, int b)
{
  return a + b;
}

PYBIND11_MODULE(pirsamp, m) {
  m.doc() = "Pi Radio Sample Buffer and Trigger classes";

  m.def("add", &add, "Stupid func");
}
