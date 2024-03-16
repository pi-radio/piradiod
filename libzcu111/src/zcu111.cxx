#include <iostream>
#include <fstream>
#include <iomanip>
#include <map>

#include <fmt/core.h>

#include <piradio/zcu111.hpp>

namespace fs = std::filesystem;

static const fs::path siprog_path{"/run/fpgad/si5382"};
static const fs::path lmkprog_path{"/run/fpgad/lmk04208"};
static const fs::path lmxA_path{"/run/fpgad/lmxA"};
static const fs::path lmxB_path{"/run/fpgad/lmxB"};
static const fs::path lmxC_path{"/run/fpgad/lmxC"};

namespace piradio
{
  extern const std::vector<unsigned int> LMK04208_122_88_regs;
  extern const std::vector<unsigned int> LMK04208_102_4_regs;
  extern const std::vector<std::tuple<uint8_t, uint8_t, uint8_t> > si_122_88;

  
  Si5382::Si5382() : i2c(zcu111_i2c::find_device(0x68), 0x68)
  {
  }

  void Si5382::write_reg(uint8_t page, uint8_t reg, uint8_t val) {
    if (page == 0xFF) {
      usleep(1000);
      return;
    }
    i2c.write(0x01, page);
    i2c.write(reg, val);
  }
  
  ZCU111::ZCU111() :
    i2c_spi(zcu111_i2c::find_LMXs(), 0x2F),
    reference_frequency(default_reference),
    zcu111_lmx_A(default_reference),
    zcu111_lmx_B(default_reference),
    zcu111_lmx_C(default_reference)
  {
    if (!fs::exists(runtime_path)) {
      fs::create_directory(runtime_path);
    }
  }

  void ZCU111::program_Si5382()
  {
    Si5382 si;

    // Note, if shit's broken, I changed this
    //i2c.write(0x01, 0x00);
    //i2c.write(0x02);
    //i2c.read(0x00);
    //i2c.write(0x03);
    //i2c.read(0x00);

    int i = 0;
    uint8_t page, reg, val;
                        
    for (auto r : si_122_88) {
      std::tie(page, reg, val) = r;

      try {
	si5382.write_reg(page, reg, val);
      } catch(...) {
	std::cout << "Write failed: " << (int)page << " " << (int)reg << " " << (int)val << std::endl;
      }
    }

    std::ofstream freq(si5382_path);
    
    freq << "122880000" << std::endl;
  }
  
  
  void ZCU111::tune_all(const frequency &freq)
  {
    zcu111_lmx_A.tune(freq, freq);
    zcu111_lmx_B.tune(freq, freq);
    zcu111_lmx_C.tune(freq, freq);

    for (int i = 0; i < 3; i++)
      program_lmx(i);
  }

  void ZCU111::dump_lmx_regs(const frequency &freq)
  {
    LMX2594 lmx(reference_frequency);
    std::map<int, uint16_t>  regs;
    
    lmx.tune(freq, freq);

    lmx.config.fill_regs(regs);

    for (int i = 112; i >= 0; i--) {
      std::cout << fmt::format("{:d} 0x{:06x}", i, regs[i]) << std::endl;
    }
  }
  
  void ZCU111::enable_clocks(void)
  {
    zcu111_lmx_A.enable_all();    
    zcu111_lmx_B.enable_all();    
    zcu111_lmx_C.enable_all();    

    for (int i = 0; i < 3; i++)
      program_lmx(i);
  }

  
  void ZCU111::mute_clocks(void)
  {
    zcu111_lmx_A.disable_all();    
    zcu111_lmx_B.disable_all();    
    zcu111_lmx_C.disable_all();    

    for (int i = 0; i < 3; i++)
      program_lmx(i);
  }
  
  void ZCU111::program_lmx(int n)
  {
    std::map<int, uint16_t> lmx_regs;

    if (n == 0 || n == -1) {
      zcu111_lmx_A.config.fill_regs(lmx_regs);

      i2c_program_lmx(8, lmx_regs);      
    } else if (n == 1 || n == -1) {
      zcu111_lmx_B.config.fill_regs(lmx_regs);

      i2c_program_lmx(4, lmx_regs);      
    } else if (n == 2 || n == -1) {
      zcu111_lmx_C.config.fill_regs(lmx_regs);

      i2c_program_lmx(1, lmx_regs);      
    } else {
      throw std::runtime_error("Invalid LMX");
    }

    
  }

  void ZCU111::program_LMK04208(const std::vector<unsigned int> &regs)
  {
    int retries = 0;
    
    for (auto r : regs) {
      int result;

      i2c_spi.write(0x2, { (uint8_t)(r >> 24), (uint8_t)(r >> 16), (uint8_t)(r >> 8), (uint8_t)r });
      
      usleep(1000);
    }

    std::ofstream os(ref_freq_path);

    os << reference_frequency.Hz() << std::endl;
  }

  
  void ZCU111::program_reference()
  {
    std::cout << "Programming " << reference_frequency << " reference..." << std::endl;
    if (reference_frequency == MHz(102.4)) {
      program_LMK04208(LMK04208_102_4_regs);
    } else if (reference_frequency == MHz(122.88)) {
      program_LMK04208(LMK04208_122_88_regs);
    } else {
      throw std::runtime_error(fmt::format("Invalid reference frequency {}", reference_frequency.MHz()));
    }
  }
  
  void ZCU111::write_i2c_spi(std::initializer_list<uint8_t> il)
  {
    uint8_t buf[32];

    
    i2c_spi.write(il);

  }

  
  void ZCU111::i2c_program_lmx(uint8_t mask, const std::map<int, uint16_t>  &regs)
  {
    int result;
    uint16_t r;

    useconds_t short_delay = 1000;
    useconds_t long_delay = 10000;
        
    r = regs.at(0);

    //i2c_spi.txn(0x2F, { mask, (uint8_t)0, (uint8_t)(r >> 8), (uint8_t)(r | 0x02) });
    usleep(short_delay);


    i2c_spi.txn(0x2F, { mask, (uint8_t)0, (uint8_t)(r >> 8), (uint8_t)(r & 0xF7) });
    usleep(100000);
    
    auto it = regs.crbegin();

    while (1) {
      int retries = 0;
      int retval;
      uint8_t addr = it->first;
      r = it->second;

      if (++it == regs.crend()) break;

#if 0
      std::cout << "R" << (int)addr << " 0x"
		<< std::hex << std::setfill('0')
		<< std::setw(2) << (int)addr
		<< std::setw(4) << r << std::dec << std::endl;
#endif
      
      i2c_spi.txn(0x2F, {mask, addr, (uint8_t)(r >> 8), (uint8_t)r });
      usleep(short_delay);
    }

    r = regs.at(0);

    i2c_spi.txn(0x2F, { mask, (uint8_t)0, (uint8_t)(r >> 8), (uint8_t)(r & 0xF7) });
    usleep(long_delay);

    i2c_spi.txn(0x2F, { mask, (uint8_t)0, (uint8_t)(r >> 8), (uint8_t)(r | 0x8) });

    usleep(short_delay);
  }

  const std::vector<unsigned int> LMK04208_122_88_regs = {
    0x00160040,0x00140320,0x80140321,0x00140322,
    0xC0140023,0x40140024,0x80141E05,0x03300006,
    0x01300007,0x06010008,0x55555549,0x9102410A,
    0x0401100B,0x1B0C006C,0x2302886D,0x0200000E,
    0x8000800F,0xC1550410,0x00000058,0x02C9C419,
    0x8FA8001A,0x10001E1B,0x0021201C,0x0180033D,
    0x0200033E,0x003F001F
  };

  const std::vector<unsigned int> LMK04208_102_4_regs = {
    0x00160040,
    0x00142580,
    0x00142581,
    0x001403C2,
    0x80142583,
    0x001403C4,
    0x00142585,
    0x01100006,
    0x01100007,
    0x06010008,
    0x55555549,
    0x9102410A,
    0x0401100B,
    0x1B0C006C,
    0x2302886D,
    0x0200000E,
    0x8000800F,
    0xC1550410,
    0x00000058,
    0x02C9C419,
    0x8FA8001A,
    0x10001E1B,
    0x0021201C,
    0x0180033D,
    0x0200033E,
    0x003F001F
  };
    
  const  std::vector<std::tuple<uint8_t, uint8_t, uint8_t> > si_122_88 = {
    { 0x0B, 0x24, 0xC0 },
    { 0x0B, 0x25, 0x04 },
    { 0x05, 0x40, 0x01 },
    {   -1,   -1,   -1 },
    { 0x00, 0x06, 0x00 },
    { 0x00, 0x07, 0x00 },
    { 0x00, 0x08, 0x00 },
    { 0x00, 0x0B, 0x68 },
    { 0x00, 0x16, 0x03 },
    { 0x00, 0x17, 0xDC },
    { 0x00, 0x18, 0xEE },
    { 0x00, 0x19, 0xFF },
    { 0x00, 0x1A, 0xFF },
    { 0x00, 0x20, 0x02 },
    { 0x00, 0x2B, 0x02 },
    { 0x00, 0x2C, 0x01 },
    { 0x00, 0x2D, 0x00 },
    { 0x00, 0x2E, 0x3C },
    { 0x00, 0x2F, 0x00 },
    { 0x00, 0x30, 0x00 },
    { 0x00, 0x31, 0x00 },
    { 0x00, 0x32, 0x00 },
    { 0x00, 0x33, 0x00 },
    { 0x00, 0x34, 0x00 },
    { 0x00, 0x35, 0x00 },
    { 0x00, 0x36, 0x02 },
    { 0x00, 0x37, 0x00 },
    { 0x00, 0x38, 0x00 },
    { 0x00, 0x39, 0x00 },
    { 0x00, 0x3A, 0x00 },
    { 0x00, 0x3B, 0x00 },
    { 0x00, 0x3C, 0x00 },
    { 0x00, 0x3D, 0x00 },
    { 0x00, 0x3E, 0x10 },
    { 0x00, 0x3F, 0x11 },
    { 0x00, 0x40, 0x04 },
    { 0x00, 0x41, 0x0D },
    { 0x00, 0x42, 0x00 },
    { 0x00, 0x43, 0x00 },
    { 0x00, 0x44, 0x00 },
    { 0x00, 0x45, 0x0C },
    { 0x00, 0x46, 0x32 },
    { 0x00, 0x47, 0x00 },
    { 0x00, 0x48, 0x00 },
    { 0x00, 0x49, 0x00 },
    { 0x00, 0x4A, 0x32 },
    { 0x00, 0x4B, 0x00 },
    { 0x00, 0x4C, 0x00 },
    { 0x00, 0x4D, 0x00 },
    { 0x00, 0x4E, 0x05 },
    { 0x00, 0x4F, 0x00 },
    { 0x00, 0x50, 0x0F },
    { 0x00, 0x51, 0x03 },
    { 0x00, 0x52, 0x00 },
    { 0x00, 0x53, 0x00 },
    { 0x00, 0x54, 0x00 },
    { 0x00, 0x55, 0x03 },
    { 0x00, 0x56, 0x00 },
    { 0x00, 0x57, 0x00 },
    { 0x00, 0x58, 0x00 },
    { 0x00, 0x59, 0x01 },
    { 0x00, 0x5A, 0x67 },
    { 0x00, 0x5B, 0x45 },
    { 0x00, 0x5C, 0x23 },
    { 0x00, 0x5D, 0x01 },
    { 0x00, 0x5E, 0x00 },
    { 0x00, 0x5F, 0x00 },
    { 0x00, 0x60, 0x00 },
    { 0x00, 0x61, 0x00 },
    { 0x00, 0x62, 0x00 },
    { 0x00, 0x63, 0x00 },
    { 0x00, 0x64, 0x00 },
    { 0x00, 0x65, 0x00 },
    { 0x00, 0x66, 0x00 },
    { 0x00, 0x67, 0x00 },
    { 0x00, 0x68, 0x00 },
    { 0x00, 0x69, 0x00 },
    { 0x00, 0x92, 0x02 },
    { 0x00, 0x93, 0xA0 },
    { 0x00, 0x95, 0x00 },
    { 0x00, 0x96, 0x80 },
    { 0x00, 0x98, 0x60 },
    { 0x00, 0x9A, 0x02 },
    { 0x00, 0x9B, 0x60 },
    { 0x00, 0x9D, 0x08 },
    { 0x00, 0x9E, 0x40 },
    { 0x00, 0xA0, 0x20 },
    { 0x00, 0xA2, 0x00 },
    { 0x00, 0xA4, 0x00 },
    { 0x00, 0xA5, 0x00 },
    { 0x00, 0xA6, 0x00 },
    { 0x00, 0xA7, 0x00 },
    { 0x00, 0xA9, 0xA5 },
    { 0x00, 0xAA, 0x61 },
    { 0x00, 0xAB, 0x00 },
    { 0x00, 0xAC, 0x00 },
    { 0x00, 0xE5, 0x21 },
    { 0x00, 0xE6, 0x00 },
    { 0x00, 0xE7, 0x00 },
    { 0x00, 0xE8, 0x00 },
    { 0x00, 0xE9, 0x00 },
    { 0x00, 0xEA, 0x0A },
    { 0x00, 0xEB, 0x60 },
    { 0x00, 0xEC, 0x00 },
    { 0x00, 0xED, 0x00 },
    { 0x01, 0x02, 0x01 },
    { 0x01, 0x03, 0x02 },
    { 0x01, 0x04, 0x09 },
    { 0x01, 0x05, 0x3E },
    { 0x01, 0x06, 0x18 },
    { 0x01, 0x07, 0x01 },
    { 0x01, 0x08, 0x01 },
    { 0x01, 0x09, 0x09 },
    { 0x01, 0x0A, 0x3B },
    { 0x01, 0x0B, 0x28 },
    { 0x01, 0x0C, 0x02 },
    { 0x01, 0x0D, 0x06 },
    { 0x01, 0x0E, 0x09 },
    { 0x01, 0x0F, 0x3E },
    { 0x01, 0x10, 0x19 },
    { 0x01, 0x11, 0x02 },
    { 0x01, 0x12, 0x01 },
    { 0x01, 0x13, 0x09 },
    { 0x01, 0x14, 0x3B },
    { 0x01, 0x15, 0x28 },
    { 0x01, 0x16, 0x02 },
    { 0x01, 0x17, 0x01 },
    { 0x01, 0x18, 0x09 },
    { 0x01, 0x19, 0x3B },
    { 0x01, 0x1A, 0x28 },
    { 0x01, 0x1B, 0x02 },
    { 0x01, 0x1C, 0x01 },
    { 0x01, 0x1D, 0x09 },
    { 0x01, 0x1E, 0x3B },
    { 0x01, 0x1F, 0x28 },
    { 0x01, 0x20, 0x02 },
    { 0x01, 0x21, 0x01 },
    { 0x01, 0x22, 0x09 },
    { 0x01, 0x23, 0x3B },
    { 0x01, 0x24, 0x28 },
    { 0x01, 0x25, 0x02 },
    { 0x01, 0x26, 0x01 },
    { 0x01, 0x27, 0x09 },
    { 0x01, 0x28, 0x3B },
    { 0x01, 0x29, 0x28 },
    { 0x01, 0x2A, 0x02 },
    { 0x01, 0x2B, 0x01 },
    { 0x01, 0x2C, 0x09 },
    { 0x01, 0x2D, 0x3B },
    { 0x01, 0x2E, 0x28 },
    { 0x01, 0x2F, 0x02 },
    { 0x01, 0x30, 0x01 },
    { 0x01, 0x31, 0x09 },
    { 0x01, 0x32, 0x3B },
    { 0x01, 0x33, 0x28 },
    { 0x01, 0x34, 0x02 },
    { 0x01, 0x35, 0x01 },
    { 0x01, 0x36, 0x09 },
    { 0x01, 0x37, 0x3B },
    { 0x01, 0x38, 0x28 },
    { 0x01, 0x39, 0x02 },
    { 0x01, 0x3A, 0x01 },
    { 0x01, 0x3B, 0x09 },
    { 0x01, 0x3C, 0x3B },
    { 0x01, 0x3D, 0x28 },
    { 0x01, 0x3E, 0x02 },
    { 0x01, 0x3F, 0x00 },
    { 0x01, 0x40, 0x00 },
    { 0x01, 0x41, 0x40 },
    { 0x01, 0x42, 0xFF },
    { 0x02, 0x08, 0x3E },
    { 0x02, 0x09, 0x00 },
    { 0x02, 0x0A, 0x00 },
    { 0x02, 0x0B, 0x00 },
    { 0x02, 0x0C, 0x00 },
    { 0x02, 0x0D, 0x00 },
    { 0x02, 0x0E, 0x01 },
    { 0x02, 0x0F, 0x00 },
    { 0x02, 0x10, 0x00 },
    { 0x02, 0x11, 0x00 },
    { 0x02, 0x12, 0x00 },
    { 0x02, 0x13, 0x00 },
    { 0x02, 0x14, 0x00 },
    { 0x02, 0x15, 0x00 },
    { 0x02, 0x16, 0x00 },
    { 0x02, 0x17, 0x00 },
    { 0x02, 0x18, 0x00 },
    { 0x02, 0x19, 0x00 },
    { 0x02, 0x1A, 0x00 },
    { 0x02, 0x1B, 0x00 },
    { 0x02, 0x1C, 0x00 },
    { 0x02, 0x1D, 0x00 },
    { 0x02, 0x1E, 0x00 },
    { 0x02, 0x1F, 0x00 },
    { 0x02, 0x20, 0x00 },
    { 0x02, 0x21, 0x00 },
    { 0x02, 0x22, 0x00 },
    { 0x02, 0x23, 0x00 },
    { 0x02, 0x24, 0x00 },
    { 0x02, 0x25, 0x00 },
    { 0x02, 0x26, 0x00 },
    { 0x02, 0x27, 0x00 },
    { 0x02, 0x28, 0x00 },
    { 0x02, 0x29, 0x00 },
    { 0x02, 0x2A, 0x00 },
    { 0x02, 0x2B, 0x00 },
    { 0x02, 0x2C, 0x00 },
    { 0x02, 0x2D, 0x00 },
    { 0x02, 0x2E, 0x00 },
    { 0x02, 0x2F, 0x00 },
    { 0x02, 0x31, 0x0B },
    { 0x02, 0x32, 0x0B },
    { 0x02, 0x33, 0x0B },
    { 0x02, 0x34, 0x0B },
    { 0x02, 0x35, 0x00 },
    { 0x02, 0x36, 0x00 },
    { 0x02, 0x37, 0x00 },
    { 0x02, 0x38, 0x00 },
    { 0x02, 0x39, 0x00 },
    { 0x02, 0x3A, 0x01 },
    { 0x02, 0x3B, 0x00 },
    { 0x02, 0x3C, 0x00 },
    { 0x02, 0x3D, 0x00 },
    { 0x02, 0x3E, 0xF0 },
    { 0x02, 0x47, 0x02 },
    { 0x02, 0x48, 0x00 },
    { 0x02, 0x49, 0x00 },
    { 0x02, 0x4A, 0x00 },
    { 0x02, 0x4B, 0x00 },
    { 0x02, 0x4C, 0x00 },
    { 0x02, 0x4D, 0x00 },
    { 0x02, 0x4E, 0x00 },
    { 0x02, 0x4F, 0x00 },
    { 0x02, 0x50, 0x00 },
    { 0x02, 0x51, 0x00 },
    { 0x02, 0x52, 0x00 },
    { 0x02, 0x53, 0x00 },
    { 0x02, 0x54, 0x00 },
    { 0x02, 0x55, 0x00 },
    { 0x02, 0x56, 0x00 },
    { 0x02, 0x57, 0x00 },
    { 0x02, 0x58, 0x00 },
    { 0x02, 0x59, 0x00 },
    { 0x02, 0x5A, 0x00 },
    { 0x02, 0x5B, 0x00 },
    { 0x02, 0x5C, 0x00 },
    { 0x02, 0x5D, 0x00 },
    { 0x02, 0x5E, 0x00 },
    { 0x02, 0x5F, 0x00 },
    { 0x02, 0x60, 0x00 },
    { 0x02, 0x61, 0x00 },
    { 0x02, 0x62, 0x00 },
    { 0x02, 0x63, 0x00 },
    { 0x02, 0x64, 0x00 },
    { 0x02, 0x65, 0x00 },
    { 0x02, 0x66, 0x00 },
    { 0x02, 0x67, 0x00 },
    { 0x02, 0x68, 0x00 },
    { 0x02, 0x69, 0x00 },
    { 0x02, 0x6A, 0x00 },
    { 0x02, 0x6B, 0x7A },
    { 0x02, 0x6C, 0x63 },
    { 0x02, 0x6D, 0x75 },
    { 0x02, 0x6E, 0x5F },
    { 0x02, 0x6F, 0x31 },
    { 0x02, 0x70, 0x32 },
    { 0x02, 0x71, 0x32 },
    { 0x02, 0x72, 0x6D },
    { 0x02, 0x8A, 0x00 },
    { 0x02, 0x8B, 0x00 },
    { 0x02, 0x8C, 0x00 },
    { 0x02, 0x8D, 0x00 },
    { 0x02, 0x8E, 0x00 },
    { 0x02, 0x8F, 0x00 },
    { 0x02, 0x90, 0x00 },
    { 0x02, 0x91, 0x00 },
    { 0x02, 0x92, 0x3F },
    { 0x02, 0x93, 0xFF },
    { 0x02, 0x94, 0xB8 },
    { 0x02, 0x96, 0x02 },
    { 0x02, 0x97, 0x02 },
    { 0x02, 0x99, 0x02 },
    { 0x02, 0x9A, 0x00 },
    { 0x02, 0x9B, 0x00 },
    { 0x02, 0x9C, 0x00 },
    { 0x02, 0x9D, 0xFA },
    { 0x02, 0x9E, 0x01 },
    { 0x02, 0x9F, 0x00 },
    { 0x02, 0xA6, 0x00 },
    { 0x02, 0xA7, 0x00 },
    { 0x02, 0xA8, 0x00 },
    { 0x02, 0xA9, 0xCC },
    { 0x02, 0xAA, 0x04 },
    { 0x02, 0xAB, 0x00 },
    { 0x02, 0xB7, 0xFF },
    { 0x02, 0xBC, 0x00 },
    { 0x03, 0x02, 0x00 },
    { 0x03, 0x03, 0x00 },
    { 0x03, 0x04, 0x00 },
    { 0x03, 0x05, 0x00 },
    { 0x03, 0x06, 0x0A },
    { 0x03, 0x07, 0x00 },
    { 0x03, 0x08, 0x00 },
    { 0x03, 0x09, 0x00 },
    { 0x03, 0x0A, 0x00 },
    { 0x03, 0x0B, 0x80 },
    { 0x03, 0x0C, 0x00 },
    { 0x03, 0x0D, 0x00 },
    { 0x03, 0x0E, 0x00 },
    { 0x03, 0x0F, 0x00 },
    { 0x03, 0x10, 0x00 },
    { 0x03, 0x11, 0x1E },
    { 0x03, 0x12, 0x00 },
    { 0x03, 0x13, 0x00 },
    { 0x03, 0x14, 0x00 },
    { 0x03, 0x15, 0x00 },
    { 0x03, 0x16, 0x80 },
    { 0x03, 0x17, 0x00 },
    { 0x03, 0x18, 0x00 },
    { 0x03, 0x19, 0x00 },
    { 0x03, 0x1A, 0x00 },
    { 0x03, 0x1B, 0x00 },
    { 0x03, 0x1C, 0x00 },
    { 0x03, 0x1D, 0x00 },
    { 0x03, 0x1E, 0x00 },
    { 0x03, 0x1F, 0x00 },
    { 0x03, 0x20, 0x00 },
    { 0x03, 0x21, 0x00 },
    { 0x03, 0x22, 0x00 },
    { 0x03, 0x23, 0x00 },
    { 0x03, 0x24, 0x00 },
    { 0x03, 0x25, 0x00 },
    { 0x03, 0x26, 0x00 },
    { 0x03, 0x27, 0x00 },
    { 0x03, 0x28, 0x00 },
    { 0x03, 0x29, 0x00 },
    { 0x03, 0x2A, 0x00 },
    { 0x03, 0x2B, 0x00 },
    { 0x03, 0x2C, 0x00 },
    { 0x03, 0x2D, 0x00 },
    { 0x03, 0x2E, 0x00 },
    { 0x03, 0x2F, 0x00 },
    { 0x03, 0x30, 0x00 },
    { 0x03, 0x31, 0x00 },
    { 0x03, 0x32, 0x00 },
    { 0x03, 0x33, 0x00 },
    { 0x03, 0x34, 0x00 },
    { 0x03, 0x35, 0x00 },
    { 0x03, 0x36, 0x00 },
    { 0x03, 0x37, 0x00 },
    { 0x03, 0x38, 0x00 },
    { 0x03, 0x3B, 0x00 },
    { 0x03, 0x3C, 0x00 },
    { 0x03, 0x3D, 0x00 },
    { 0x03, 0x3E, 0x00 },
    { 0x03, 0x3F, 0x00 },
    { 0x03, 0x40, 0x00 },
    { 0x03, 0x5B, 0x00 },
    { 0x03, 0x5C, 0x01 },
    { 0x03, 0x5D, 0x00 },
    { 0x03, 0x5E, 0x00 },
    { 0x03, 0x5F, 0x00 },
    { 0x03, 0x60, 0x00 },
    { 0x03, 0x61, 0x00 },
    { 0x03, 0x62, 0x00 },
    { 0x04, 0x08, 0x00 },
    { 0x04, 0x09, 0x00 },
    { 0x04, 0x0A, 0x00 },
    { 0x04, 0x0B, 0x00 },
    { 0x04, 0x0C, 0x00 },
    { 0x04, 0x0D, 0x00 },
    { 0x04, 0x0E, 0x00 },
    { 0x04, 0x0F, 0x00 },
    { 0x04, 0x10, 0x00 },
    { 0x04, 0x11, 0x00 },
    { 0x04, 0x12, 0x00 },
    { 0x04, 0x13, 0x00 },
    { 0x04, 0x15, 0x00 },
    { 0x04, 0x16, 0x00 },
    { 0x04, 0x17, 0x00 },
    { 0x04, 0x18, 0x00 },
    { 0x04, 0x19, 0x00 },
    { 0x04, 0x1A, 0x00 },
    { 0x04, 0x1B, 0x00 },
    { 0x04, 0x1C, 0x00 },
    { 0x04, 0x1D, 0x00 },
    { 0x04, 0x1E, 0x00 },
    { 0x04, 0x1F, 0x00 },
    { 0x04, 0x21, 0x2B },
    { 0x04, 0x22, 0x01 },
    { 0x04, 0x23, 0x00 },
    { 0x04, 0x24, 0x00 },
    { 0x04, 0x25, 0x00 },
    { 0x04, 0x26, 0x00 },
    { 0x04, 0x27, 0x00 },
    { 0x04, 0x28, 0x00 },
    { 0x04, 0x29, 0x00 },
    { 0x04, 0x2A, 0x00 },
    { 0x04, 0x2B, 0x01 },
    { 0x04, 0x2C, 0x0F },
    { 0x04, 0x2D, 0x03 },
    { 0x04, 0x2E, 0x00 },
    { 0x04, 0x2F, 0x00 },
    { 0x04, 0x31, 0x00 },
    { 0x04, 0x32, 0x00 },
    { 0x04, 0x33, 0x04 },
    { 0x04, 0x34, 0x00 },
    { 0x04, 0x35, 0x01 },
    { 0x04, 0x36, 0x06 },
    { 0x04, 0x37, 0x00 },
    { 0x04, 0x38, 0x00 },
    { 0x04, 0x39, 0x00 },
    { 0x04, 0x3D, 0x0A },
    { 0x04, 0x3E, 0x06 },
    { 0x04, 0x87, 0x00 },
    { 0x04, 0x88, 0x00 },
    { 0x04, 0x89, 0x00 },
    { 0x04, 0x8A, 0x00 },
    { 0x04, 0x8B, 0x00 },
    { 0x04, 0x8C, 0x00 },
    { 0x04, 0x8D, 0x00 },
    { 0x04, 0x9B, 0x18 },
    { 0x04, 0x9C, 0x4C },
    { 0x04, 0x9D, 0x00 },
    { 0x04, 0x9E, 0x00 },
    { 0x04, 0x9F, 0x00 },
    { 0x04, 0xA0, 0x00 },
    { 0x04, 0xA1, 0x00 },
    { 0x04, 0xA2, 0x00 },
    { 0x04, 0xA4, 0x20 },
    { 0x04, 0xA5, 0x00 },
    { 0x04, 0xA6, 0x00 },
    { 0x04, 0xAC, 0x00 },
    { 0x04, 0xAD, 0x00 },
    { 0x04, 0xAE, 0x00 },
    { 0x04, 0xB1, 0x00 },
    { 0x04, 0xB2, 0x00 },
    { 0x05, 0x08, 0x0E },
    { 0x05, 0x09, 0x1D },
    { 0x05, 0x0A, 0x0C },
    { 0x05, 0x0B, 0x0B },
    { 0x05, 0x0C, 0x3F },
    { 0x05, 0x0D, 0x0F },
    { 0x05, 0x0E, 0x11 },
    { 0x05, 0x0F, 0x25 },
    { 0x05, 0x10, 0x09 },
    { 0x05, 0x11, 0x08 },
    { 0x05, 0x12, 0x3F },
    { 0x05, 0x13, 0x0F },
    { 0x05, 0x15, 0x00 },
    { 0x05, 0x16, 0x00 },
    { 0x05, 0x17, 0x00 },
    { 0x05, 0x18, 0x00 },
    { 0x05, 0x19, 0xE8 },
    { 0x05, 0x1A, 0x02 },
    { 0x05, 0x1B, 0x00 },
    { 0x05, 0x1C, 0x00 },
    { 0x05, 0x1D, 0x00 },
    { 0x05, 0x1E, 0x00 },
    { 0x05, 0x1F, 0x80 },
    { 0x05, 0x21, 0x0B },
    { 0x05, 0x2A, 0x01 },
    { 0x05, 0x2B, 0x01 },
    { 0x05, 0x2C, 0x87 },
    { 0x05, 0x2D, 0x03 },
    { 0x05, 0x2E, 0x19 },
    { 0x05, 0x2F, 0x19 },
    { 0x05, 0x31, 0x00 },
    { 0x05, 0x32, 0x49 },
    { 0x05, 0x33, 0x03 },
    { 0x05, 0x34, 0x00 },
    { 0x05, 0x36, 0x04 },
    { 0x05, 0x37, 0x00 },
    { 0x05, 0x38, 0x00 },
    { 0x05, 0x39, 0x00 },
    { 0x05, 0x3A, 0x01 },
    { 0x05, 0x3B, 0x03 },
    { 0x05, 0x3C, 0x00 },
    { 0x05, 0x3D, 0x04 },
    { 0x05, 0x3E, 0x02 },
    { 0x05, 0x88, 0x07 },
    { 0x05, 0x89, 0x0D },
    { 0x05, 0x8A, 0x00 },
    { 0x05, 0x8B, 0xA2 },
    { 0x05, 0x8C, 0x56 },
    { 0x05, 0x8D, 0x00 },
    { 0x05, 0x9B, 0x7A },
    { 0x05, 0x9C, 0x8C },
    { 0x05, 0x9D, 0x0E },
    { 0x05, 0x9E, 0x1F },
    { 0x05, 0x9F, 0x0C },
    { 0x05, 0xA0, 0x0B },
    { 0x05, 0xA1, 0x3F },
    { 0x05, 0xA2, 0x0F },
    { 0x05, 0xA4, 0x08 },
    { 0x05, 0xA5, 0x00 },
    { 0x05, 0xA6, 0x03 },
    { 0x05, 0xAC, 0x09 },
    { 0x05, 0xAD, 0xE7 },
    { 0x05, 0xAE, 0x45 },
    { 0x05, 0xB1, 0xDD },
    { 0x05, 0xB2, 0x02 },
    { 0x08, 0x02, 0x35 },
    { 0x08, 0x03, 0x04 },
    { 0x08, 0x04, 0x01 },
    { 0x08, 0x05, 0x53 },
    { 0x08, 0x06, 0x0B },
    { 0x08, 0x07, 0x10 },
    { 0x08, 0x08, 0x00 },
    { 0x08, 0x09, 0x00 },
    { 0x08, 0x0A, 0x00 },
    { 0x08, 0x0B, 0x00 },
    { 0x08, 0x0C, 0x00 },
    { 0x08, 0x0D, 0x00 },
    { 0x08, 0x0E, 0x00 },
    { 0x08, 0x0F, 0x00 },
    { 0x08, 0x10, 0x00 },
    { 0x08, 0x11, 0x00 },
    { 0x08, 0x12, 0x00 },
    { 0x08, 0x13, 0x00 },
    { 0x08, 0x14, 0x00 },
    { 0x08, 0x15, 0x00 },
    { 0x08, 0x16, 0x00 },
    { 0x08, 0x17, 0x00 },
    { 0x08, 0x18, 0x00 },
    { 0x08, 0x19, 0x00 },
    { 0x08, 0x1A, 0x00 },
    { 0x08, 0x1B, 0x00 },
    { 0x08, 0x1C, 0x00 },
    { 0x08, 0x1D, 0x00 },
    { 0x08, 0x1E, 0x00 },
    { 0x08, 0x1F, 0x00 },
    { 0x08, 0x20, 0x00 },
    { 0x08, 0x21, 0x00 },
    { 0x08, 0x22, 0x00 },
    { 0x08, 0x23, 0x00 },
    { 0x08, 0x24, 0x00 },
    { 0x08, 0x25, 0x00 },
    { 0x08, 0x26, 0x00 },
    { 0x08, 0x27, 0x00 },
    { 0x08, 0x28, 0x00 },
    { 0x08, 0x29, 0x00 },
    { 0x08, 0x2A, 0x00 },
    { 0x08, 0x2B, 0x00 },
    { 0x08, 0x2C, 0x00 },
    { 0x08, 0x2D, 0x00 },
    { 0x08, 0x2E, 0x00 },
    { 0x08, 0x2F, 0x00 },
    { 0x08, 0x30, 0x00 },
    { 0x08, 0x31, 0x00 },
    { 0x08, 0x32, 0x00 },
    { 0x08, 0x33, 0x00 },
    { 0x08, 0x34, 0x00 },
    { 0x08, 0x35, 0x00 },
    { 0x08, 0x36, 0x00 },
    { 0x08, 0x37, 0x00 },
    { 0x08, 0x38, 0x00 },
    { 0x08, 0x39, 0x00 },
    { 0x08, 0x3A, 0x00 },
    { 0x08, 0x3B, 0x00 },
    { 0x08, 0x3C, 0x00 },
    { 0x08, 0x3D, 0x00 },
    { 0x08, 0x3E, 0x00 },
    { 0x08, 0x3F, 0x00 },
    { 0x08, 0x40, 0x00 },
    { 0x08, 0x41, 0x00 },
    { 0x08, 0x42, 0x00 },
    { 0x08, 0x43, 0x00 },
    { 0x08, 0x44, 0x00 },
    { 0x08, 0x45, 0x00 },
    { 0x08, 0x46, 0x00 },
    { 0x08, 0x47, 0x00 },
    { 0x08, 0x48, 0x00 },
    { 0x08, 0x49, 0x00 },
    { 0x08, 0x4A, 0x00 },
    { 0x08, 0x4B, 0x00 },
    { 0x08, 0x4C, 0x00 },
    { 0x08, 0x4D, 0x00 },
    { 0x08, 0x4E, 0x00 },
    { 0x08, 0x4F, 0x00 },
    { 0x08, 0x50, 0x00 },
    { 0x08, 0x51, 0x00 },
    { 0x08, 0x52, 0x00 },
    { 0x08, 0x53, 0x00 },
    { 0x08, 0x54, 0x00 },
    { 0x08, 0x55, 0x00 },
    { 0x08, 0x56, 0x00 },
    { 0x08, 0x57, 0x00 },
    { 0x08, 0x58, 0x00 },
    { 0x08, 0x59, 0x00 },
    { 0x08, 0x5A, 0x00 },
    { 0x08, 0x5B, 0x00 },
    { 0x08, 0x5C, 0x00 },
    { 0x08, 0x5D, 0x00 },
    { 0x08, 0x5E, 0x00 },
    { 0x08, 0x5F, 0x00 },
    { 0x08, 0x60, 0x00 },
    { 0x08, 0x61, 0x00 },
    { 0x09, 0x0E, 0x03 },
    { 0x09, 0x43, 0x01 },
    { 0x09, 0x49, 0x01 },
    { 0x09, 0x4A, 0x01 },
    { 0x09, 0x4E, 0x49 },
    { 0x09, 0x4F, 0xF2 },
    { 0x09, 0x5E, 0x00 },
    { 0x0A, 0x02, 0x00 },
    { 0x0A, 0x03, 0x03 },
    { 0x0A, 0x04, 0x02 },
    { 0x0A, 0x05, 0x03 },
    { 0x0A, 0x1A, 0x00 },
    { 0x0A, 0x20, 0x00 },
    { 0x0A, 0x26, 0x00 },
    { 0x0A, 0x2C, 0x00 },
    { 0x0A, 0x3C, 0x00 },
    { 0x0A, 0x3D, 0x00 },
    { 0x0A, 0x3E, 0x00 },
    { 0x0A, 0x40, 0x00 },
    { 0x0A, 0x41, 0x00 },
    { 0x0A, 0x42, 0x00 },
    { 0x0A, 0x44, 0x00 },
    { 0x0A, 0x45, 0x00 },
    { 0x0A, 0x46, 0x00 },
    { 0x0A, 0x48, 0x00 },
    { 0x0A, 0x49, 0x00 },
    { 0x0A, 0x4A, 0x00 },
    { 0x0A, 0x50, 0x00 },
    { 0x0A, 0x51, 0x00 },
    { 0x0A, 0x52, 0x00 },
    { 0x0A, 0x53, 0x00 },
    { 0x0A, 0x54, 0x00 },
    { 0x0A, 0x55, 0x00 },
    { 0x0A, 0x56, 0x00 },
    { 0x0A, 0x57, 0x00 },
    { 0x0A, 0x58, 0x00 },
    { 0x0A, 0x59, 0x00 },
    { 0x0A, 0x5A, 0x00 },
    { 0x0A, 0x5B, 0x00 },
    { 0x0A, 0x5C, 0x00 },
    { 0x0A, 0x5D, 0x00 },
    { 0x0A, 0x5E, 0x00 },
    { 0x0A, 0x5F, 0x00 },
    { 0x0B, 0x44, 0x2F },
    { 0x0B, 0x45, 0x00 },
    { 0x0B, 0x46, 0x00 },
    { 0x0B, 0x47, 0x0E },
    { 0x0B, 0x48, 0x0E },
    { 0x0B, 0x4A, 0x1C },
    { 0x0B, 0x53, 0x10 },
    { 0x0B, 0x57, 0xF0 },
    { 0x0B, 0x58, 0x00 },
    { 0x0C, 0x02, 0x03 },
    { 0x0C, 0x03, 0x01 },
    { 0x0C, 0x05, 0x00 },
    { 0x0C, 0x06, 0x00 },
    { 0x0C, 0x07, 0x01 },
    { 0x0C, 0x08, 0x01 },
    {   -1,   -1,   -1 },
    { 0x05, 0x14, 0x01 },
    { 0x00, 0x1C, 0x01 },
    { 0x05, 0x40, 0x00 },
    { 0x0B, 0x24, 0xC3 },
    { 0x0B, 0x25, 0x06 }
  };
};
         
