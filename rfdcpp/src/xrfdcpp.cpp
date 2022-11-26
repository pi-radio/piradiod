#include <iostream>
#include <fstream>
#include <filesystem>
#include <assert.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

#include <xrfdcpp/xrfdcpp.hpp>

namespace fs = std::filesystem;

struct rftile_csr
{
  uint32_t rsrved0000;
  uint32_t restart_posm;
  uint32_t restart_state;
  uint32_t current_state;
  uint32_t pad0010[(0x0038-0x0010)/4];
  uint32_t reset_count;
  uint32_t pad003C[(0x0080-0x0038)/4];
  uint32_t clock_detect;
  uint32_t pad0088[(0x0100-0x0088)/4];
  uint32_t post_impl_sim_speedup_reg;
  uint32_t pad0104[(0x0200-0x0104)/4];
  uint32_t isr;
  uint32_t ier;
  uint32_t conv0_intr;
  uint32_t conv0_intr_en;
  uint32_t conv1_intr;
  uint32_t conv1_intr_en;
  uint32_t conv2_intr;
  uint32_t conv2_intr_en;
  uint32_t conv3_intr;
  uint32_t conv3_intr_en;
  uint32_t common_status;
  uint32_t pad022C;
  uint32_t disable;
  uint32_t pad[(0x4000 - 0x0234)/4];
} __attribute__((packed));


struct rfdc_csr
{
  uint32_t version;
  uint32_t master_reset;
  uint32_t cisr;
  uint32_t cier;
  uint32_t pad[0x4000/4 - 4];
  rftile_csr dacs[4];
  rftile_csr adcs[4];
  uint32_t pad2[(0x40000-0x24000)/4];
} __attribute__((packed));

XRFDCTile::XRFDCTile(volatile rftile_csr *_csr) : csr(_csr)
{
}

uint32_t XRFDCTile::state()
{
  return csr->current_state;
}

bool XRFDCTile::cdetect_status()
{
  return (csr->clock_detect & 1) ? true : false;
}


bool XRFDCTile::clock_detected()
{
  return (csr->common_status & 1) ? true : false;
}

bool XRFDCTile::supplies_up()
{
  return (csr->common_status & 2) ? true : false;
}

bool XRFDCTile::power_up()
{
  return (csr->common_status & 4) ? true : false;
}

bool XRFDCTile::pll_locked()
{
  return (csr->common_status & 8) ? true : false;
}
		       


XilinxRFDC::XilinxRFDC() : uio_fd(-1), csr(NULL)
{
  std::cout << std::hex << sizeof(rftile_csr) << std::endl;
  std::cout << sizeof(rfdc_csr) << std::endl;
  
  assert(sizeof(rftile_csr) == 0x4000);
  assert(sizeof(rfdc_csr) == 0x40000);
  
  std::cout << "Searching for RFDC..." << std::endl;

  fs::path dev_path("/sys/devices/platform/axi");
  fs::path rfdc_path;
  std::string uio_name;
  
  for (auto const &dir_entry : fs::directory_iterator{dev_path}) {
    if (dir_entry.path().extension() == ".usp_rf_data_converter") {
      rfdc_path = dir_entry.path();
    }
  }

  if (rfdc_path.empty()) {
    throw std::runtime_error("Could not find RF data converter device");
  }
  
  std::cout << "Found data converter at " << rfdc_path << std::endl;

  for (auto const &dir_entry : fs::directory_iterator{rfdc_path / "uio"}) {
    if (dir_entry.path().filename().string().find("uio") == 0) {
      uio_name = dir_entry.path().filename();
    } else {
      std::cerr << "Unknown entry in uio dir: " << dir_entry << std::endl;
    }
  }

  if (uio_name.length() == 0) {
    throw std::runtime_error("Could not find UIO device");
  }

  uio_fd = open((fs::path("/dev") / uio_name).c_str(), O_RDWR);

  if (uio_fd < 0) {
    throw std::runtime_error("Could not open UIO device");
  }

  fs::path uio_dir = fs::path("/sys/class/uio") / uio_name;

  // TODO -- ensure only one map
  
  fs::path map_dir = uio_dir / "maps" / "map0";

  std::ifstream addr_f(map_dir / "addr");
  std::ifstream offset_f(map_dir / "offset");
  std::ifstream size_f(map_dir / "size");

  uint64_t addr;
  uint64_t offset;
  uint64_t size;

  addr_f >> std::hex >> addr;
  offset_f >> std::hex >> offset;
  size_f >> std::hex >> csr_len;

  std::cout << "Addr: " << addr << " offset " << offset << " size " << csr_len << std::endl;

  csr = (rfdc_csr *)mmap(NULL, csr_len, PROT_READ | PROT_WRITE, MAP_SHARED, uio_fd, 0);

  if (csr == MAP_FAILED) {
    throw std::runtime_error("Failed to map CSR");
  }
  //csr = mmap
}

XilinxRFDC::~XilinxRFDC()
{
  if (csr) {
    munmap((void *)csr, csr_len);
  }

  close(uio_fd);
}

std::tuple<int, int, int, int> XilinxRFDC::version()
{
  uint32_t v = csr->version;
  
  return std::make_tuple((v>>24)&0xFF, (v>>16)&0xFF, (v>>8)&0xFF, v&0xFF);
}

void XilinxRFDC::reset()
{
  csr->master_reset = 1;
}
  


XRFDCTile XilinxRFDC::adc(int n)
{
  assert(n >= 0 && n < 4);
  return XRFDCTile(&csr->adcs[n]);
}

XRFDCTile XilinxRFDC::dac(int n)
{
  assert(n >= 0 && n < 4);
  return XRFDCTile(&csr->dacs[n]);
}
