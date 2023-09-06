#include <iostream>
#include <fstream>
#include <map>

#include <grpc/grpc.h>
#include <grpcpp/security/server_credentials.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>

#include "zcu111.grpc.pb.h"

#include <piradio/daemon.hpp>
#include <piradio/zcu111.hpp>
#include <piradio/rfdc_tile.hpp>

namespace fs = std::filesystem;

static const fs::path siprog_path{"/run/fpgad/si5382"};
static const fs::path lmkprog_path{"/run/fpgad/lmk04208"};
static const fs::path lmxA_path{"/run/fpgad/lmxA"};
static const fs::path lmxB_path{"/run/fpgad/lmxB"};
static const fs::path lmxC_path{"/run/fpgad/lmxC"};

namespace piradio
{    
  ZCU111Manager::ZCU111Manager() :
    i2c_si5382(zcu111_i2c::find_device(0x68), 0x68),
    i2c_spi(zcu111_i2c::find_device(0x2F), 0x2F),
    zcu111_lmx_A(MHz(122.88)),
    zcu111_lmx_B(MHz(122.88)),
    zcu111_lmx_C(MHz(122.88))
  {    
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
  }

  void ZCU111Manager::mute_clocks(void)
  {
    zcu111_lmx_A.disable_all();    
    zcu111_lmx_B.disable_all();    
    zcu111_lmx_C.disable_all();    

    for (int i = 0; i < 3; i++)
      program_lmx(i);

    {
      runfile r(lmxA_path);
      r << "mute mute" << std::endl;
    }
    
    {
      runfile r(lmxB_path);
      r << "mute mute" << std::endl;
    }

    {
      runfile r(lmxC_path);
      r << "mute mute" << std::endl;
    }
  }

  void check_frequency(const fs::path &path, frequency A, frequency B, bool &program)
  {
    if (program == false && fs::exists(path)) {
      runfile r(path);
      
      frequency a = -1, b = -1;

      try {
	r >> a >> b;
      } catch(std::runtime_error &e) {
	program = true;
      }
      
      if (a != A || b != B) {
	program = true;
      }
    }

  }
  
  void ZCU111Manager::tune_clocks(RFDC *rfdc, bool program)
  {
    frequency fA_A = rfdc->get_adc_tile(0)->ref_clk_freq();
    frequency fA_B = rfdc->get_adc_tile(1)->ref_clk_freq();
    frequency fB_A = rfdc->get_adc_tile(2)->ref_clk_freq();
    frequency fB_B = rfdc->get_adc_tile(3)->ref_clk_freq();
    frequency fC_A = rfdc->get_dac_tile(0)->ref_clk_freq();
    frequency fC_B = rfdc->get_dac_tile(1)->ref_clk_freq();

    zcu111_lmx_A.tune(fA_A, fA_B);
    zcu111_lmx_B.tune(fB_A, fB_B);
    zcu111_lmx_C.tune(fC_A, fC_B);

    zcu111_lmx_A.enable_all();    
    zcu111_lmx_B.enable_all();    
    zcu111_lmx_C.enable_all();

    check_frequency(lmxA_path, fA_A, fA_B, program);
    check_frequency(lmxB_path, fB_A, fB_B, program);
    check_frequency(lmxC_path, fC_A, fC_B, program);
    
    if (!program) {
      return;
    }
  
    for (int i = 0; i < 3; i++)
      program_lmx(i);
    
    {
      runfile r(lmxA_path);
      r << fA_A << " " << fA_B << std::endl;
    }
    
    {
      runfile r(lmxB_path);
      r << fB_A << " " << fB_B << std::endl;
    }
    
    {
      runfile r(lmxC_path);
      r << fC_A << " " << fC_B << std::endl;
    }
  }

  void ZCU111Manager::program_lmx(int n)
  {
    std::map<int, uint16_t> lmx_regs;

    if (n == 0) {
      zcu111_lmx_A.config.fill_regs(lmx_regs);
    } else if (n == 1) {
      zcu111_lmx_B.config.fill_regs(lmx_regs);
    } else if (n == 2) {
      zcu111_lmx_C.config.fill_regs(lmx_regs);
    } else {
      throw std::runtime_error("Invalid LMX");
    }

    
  }
}
