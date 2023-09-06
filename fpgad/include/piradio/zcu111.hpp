#pragma once

#include <piradio/lmx2594.hpp>
#include <piradio/i2c.hpp>
#include <piradio/clocks.hpp>
#include <piradio/rfdc.hpp>

namespace piradio
{
  class ZCU111Service;
  
  class ZCU111Manager
  {
  public:
    grpc::Service *grpc_service();

    ZCU111Manager();

    void mute_clocks(void);

    void tune_clocks(RFDC *rfdc, bool program=true);
          
  protected:
    LMX2594 zcu111_lmx_A;
    LMX2594 zcu111_lmx_B;
    LMX2594 zcu111_lmx_C;
    zcu111_i2c i2c_si5382;
    zcu111_i2c i2c_spi;
    
    ZCU111Service *service;

    void program_lmx(int n);
  };
}
