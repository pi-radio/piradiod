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
    i2c_spi(zcu111_i2c::find_LMXs(), 0x2F),
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

  void ZCU111::write_i2c_spi(std::initializer_list<uint8_t> il)
  {
    uint8_t buf[32];

    
    i2c_spi.write(il);

  }

  
  void ZCU111::i2c_program_lmx(uint8_t mask, const std::map<int, uint16_t>  &regs)
  {
    int result;
    uint16_t r;
    std::cout << "Programming LMX" << std::endl;

    useconds_t short_delay = 1000;
    useconds_t long_delay = 10000;
        
    std::cout << "Mask: " << (int)mask << std::endl;

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
};
         
