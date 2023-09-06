#pragma once

#include <piradio/rfdc.hpp>

namespace piradio
{
  class RFDCService;
  
  class RFDCManager
  {
  public:
    grpc::Service *grpc_service();

    RFDCManager();

    void attach_rfdc();
    void startup_rfdc();
    void shutdown_rfdc();
    
    RFDC *rfdc();
        
  protected:
    RFDC *_rfdc;
    RFDCService *service;
  };
}
