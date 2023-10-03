#pragma once

#include <piradio/lmx2594.hpp>
#include <piradio/clocks.hpp>
#include <piradio/rfdc.hpp>
#include <piradio/zcu111.hpp>

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
    ZCU111 zcu111;    
    ZCU111Service *service;
  };
}
