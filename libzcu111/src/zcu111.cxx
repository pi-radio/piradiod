#include <iostream>
#include <fstream>
#include <iomanip>
#include <map>

#include <piradio/zcu111.hpp>

namespace fs = std::filesystem;

static const fs::path siprog_path{"/run/fpgad/si5382"};
static const fs::path lmkprog_path{"/run/fpgad/lmk04208"};
static const fs::path lmxA_path{"/run/fpgad/lmxA"};
static const fs::path lmxB_path{"/run/fpgad/lmxB"};
static const fs::path lmxC_path{"/run/fpgad/lmxC"};

namespace piradio
{
  Si5382::Si5382() : i2c(zcu111_i2c::find_device(0x68), 0x68)
  {
  }

  
  ZCU111::ZCU111() :
    i2c_spi(zcu111_i2c::find_device(0x2F), 0x2F),
    zcu111_lmx_A(MHz(122.88)),
    zcu111_lmx_B(MHz(122.88)),
    zcu111_lmx_C(MHz(122.88))
  {
  }

  void ZCU111::tune_all(const frequency &freq)
  {
    zcu111_lmx_A.tune(freq, freq);
    zcu111_lmx_B.tune(freq, freq);
    zcu111_lmx_C.tune(freq, freq);

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

  void save_regs(const std::map<int, uint16_t> &regs)
  {
    std::ofstream regfile("regs.txt");
    
    for (auto it = regs.crbegin(); it != regs.crend(); it++) {
      uint8_t addr = it->first;
      uint16_t r = it->second;

      regfile << "R" << std::dec << std::setw(0) << int(addr) << " 0x" <<
	std::hex << std::setfill('0') << std::setw(2) << int(addr) << std::setw(4) << r << std::endl;
    }
  }
  
  void ZCU111::program_lmx(int n)
  {
    std::map<int, uint16_t> lmx_regs;

    if (n == 0 || n == -1) {
      zcu111_lmx_A.config.fill_regs(lmx_regs);

      i2c_program_lmx(0, lmx_regs);      
    } else if (n == 1 || n == -1) {
      zcu111_lmx_B.config.fill_regs(lmx_regs);

      i2c_program_lmx(1, lmx_regs);      
    } else if (n == 2 || n == -1) {
      zcu111_lmx_C.config.fill_regs(lmx_regs);

      i2c_program_lmx(2, lmx_regs);      
    } else {
      throw std::runtime_error("Invalid LMX");
    }

    
  }

  void ZCU111::i2c_program_lmx(int n, const std::map<int, uint16_t>  &regs)
  {
    std::cout << "Programming LMX" << std::endl;

    uint8_t mask = 0;
    
    if (n == 0) {
      mask = 8;
    } else if (n == 1) {
      mask = 4;
    } else if (n == 2) {
      mask = 1;
    } else {
      throw std::runtime_error("Invalid LMX");
    }

    
    i2c_spi.write(mask, { 0, 0, 2 });
    usleep(1000);

    i2c_spi.write(mask, { 0, 0, 0 });
    usleep(1000);

    auto it = regs.crbegin();

    while (1) {
      uint8_t addr = it->first;
      uint16_t r = it->second;

      if (++it == regs.crend()) break;
      
      i2c_spi.write(mask, {addr, (uint8_t)(r >> 8), (uint8_t)r });
    }

    uint16_t r = regs.at(0);

    i2c_spi.write(mask, { (uint8_t)0, (uint8_t)(r >> 8), (uint8_t)(r & ~0x8) });
        
    usleep(10000);

    i2c_spi.write(mask, { (uint8_t)0, (uint8_t)(r >> 8), (uint8_t)(r | 0x8) });

    usleep(1000);
  }

  
  /*
	if (!fs::exists(siprog_path)) {
	program_Si5382(i2c_si5382, si_122_88);
	
	runfile ofs(siprog_path);
	
	ofs << "programmed" << std::endl;
	}
	
    if (!fs::exists(lmkprog_path)) {
    program_LMK04208(i2c_spi, LMK04208_regs);
    
    runfile ofs(lmkprog_path);
    
    ofs << "programmed" << std::endl;
    }

    
    zcu111_lmx_A.config.read_regs(LMX4GHz_template);
    zcu111_lmx_B.config.read_regs(LMX4GHz_template);
    zcu111_lmx_C.config.read_regs(LMX4GHz_template);
      */
};
         
