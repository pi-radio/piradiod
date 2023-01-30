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
#include <xrfdcpp/config.hpp>
#include <xrfdcpp/regs.hpp>

namespace fs = std::filesystem;

using namespace rfdc;

#define ASSERT_OFFSETOF(class, member, offset) \
    static_assert(offsetof(class, member) == offset, "The offset of " #member " is not " #offset "...")

RFDC::RFDC() : uio_fd(-1), csr(NULL)
{
#define XRFDC_ADC_TILE 1
#define XRFDC_DAC_TILE 2

#define XRFDC_CTRL_STATS_OFFSET 0x0U


#define XRFDC_DAC_TILE_DRP_ADDR(X) (0x6000U + (X * 0x4000U))
#define XRFDC_DAC_TILE_CTRL_STATS_ADDR(X) (0x4000U + (X * 0x4000U))
#define XRFDC_ADC_TILE_DRP_ADDR(X) (0x16000U + (X * 0x4000U))
#define XRFDC_ADC_TILE_CTRL_STATS_ADDR(X) (0x14000U + (X * 0x4000U))
#define XRFDC_HSCOM_ADDR 0x1C00U
#define XRFDC_BLOCK_ADDR_OFFSET(X) (X * 0x400U)
#define XRFDC_TILE_DRP_OFFSET 0x2000U

#define XRFDC_DRP_BASE(type, tile)                                                                                     \
	((type) == XRFDC_ADC_TILE ? XRFDC_ADC_TILE_DRP_ADDR(tile) : XRFDC_DAC_TILE_DRP_ADDR(tile))

#define XRFDC_CTRL_STS_BASE(Type, Tile)                                                                                \
	((Type) == XRFDC_ADC_TILE ? XRFDC_ADC_TILE_CTRL_STATS_ADDR(Tile) : XRFDC_DAC_TILE_CTRL_STATS_ADDR(Tile))

#define XRFDC_BLOCK_BASE(Type, Tile, Block)                                                                            \
	((Type) == XRFDC_ADC_TILE ? (XRFDC_ADC_TILE_DRP_ADDR(Tile) + XRFDC_BLOCK_ADDR_OFFSET(Block)) :                 \
				    (XRFDC_DAC_TILE_DRP_ADDR(Tile) + XRFDC_BLOCK_ADDR_OFFSET(Block)))

  static_assert(sizeof(csr::adc) == 0x400);
  static_assert(sizeof(csr::dac) == 0x400);
  static_assert(sizeof(csr::tile) == 0x2000);
  static_assert(sizeof(csr::dac_tile) == 0x4000);
  static_assert(sizeof(csr::adc_tile) == 0x4000);
  static_assert(sizeof(csr::rfdc) == 0x40000);
  
  ASSERT_OFFSETOF(csr::rfdc, pad_0x24000, 0x24000);

  ASSERT_OFFSETOF(csr::rfdc, dac_tiles[0], XRFDC_DAC_TILE_CTRL_STATS_ADDR(0));
  ASSERT_OFFSETOF(csr::rfdc, adc_tiles[0], XRFDC_ADC_TILE_CTRL_STATS_ADDR(0));

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

  int pl_fd = open((rfdc_path / "of_node" / "param-list").c_str(), O_RDONLY);
  
  read(pl_fd, &config, sizeof(config));

  close(pl_fd);

  //std::cout << config;

  if (config.ip_type == 2) {
    generation = 3;
  } else {
    // Check for ADC type
    generation = 1;
  }

  n_adc_tiles = 0;
  n_adc_slices = 0;
  
  for (int i = 0; i < 4; i++) {
    if (config.adcs[i].num_slices != 0) {
      n_adc_tiles++;

      if (n_adc_tiles == 1) {
	n_adc_slices = config.adcs[i].num_slices;
      } else {
	assert(n_adc_slices == config.adcs[i].num_slices);
      }
    }
  }

  n_dac_tiles = 0;
  n_dac_slices = 0;
  
  for (int i = 0; i < 4; i++) {
    if (config.dacs[i].num_slices != 0) {
      n_dac_tiles++;

      if (n_dac_tiles == 1) {
	n_dac_slices = config.dacs[i].num_slices;
      } else {
	assert(n_dac_slices == config.dacs[i].num_slices);
      }
    }
  }

  
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
  
  csr = (csr::rfdc *)mmap(NULL, csr_len, PROT_READ | PROT_WRITE, MAP_SHARED, uio_fd, 0);

  if (csr == MAP_FAILED) {
    throw std::runtime_error("Failed to map CSR");
  }

  for (int i = 0; i < n_adc_tiles; i++) {
    tile_params<cfg::adc, csr::adc_tile> p(*this, i, config.adcs[i], &csr->adc_tiles[i]);
    
    adc_tiles.emplace_back(std::make_shared<ADCTile>(p));

    for (auto adc: adc_tiles.back()->get_slices()) {
      adcs.emplace_back(adc);
    }
  }

  for (int i = 0; i < n_dac_tiles; i++) {
    tile_params<cfg::dac, csr::dac_tile> p(*this, i, config.dacs[i], &csr->dac_tiles[i]);

    dac_tiles.emplace_back(std::make_shared<DACTile>(p));
  
    for (auto dac: dac_tiles.back()->get_slices()) {
      dacs.emplace_back(dac);
    }
  }
}

RFDC::~RFDC()
{
  if (csr) {
    munmap((void *)csr, csr_len);
  }

  close(uio_fd);
}

std::tuple<int, int, int, int> RFDC::version()
{
  uint32_t v = csr->version;
  
  return std::make_tuple((v>>24)&0xFF, (v>>16)&0xFF, (v>>8)&0xFF, v&0xFF);
}

void RFDC::reset()
{
  csr->master_reset = 1;
}
