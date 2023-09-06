#include <iostream>
#include <fstream>
#include <map>

#include <grpc/grpc.h>
#include <grpcpp/security/server_credentials.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>

#include "rfdcd.grpc.pb.h"

#include <piradio/rfdc_manager.hpp>

namespace fs = std::filesystem;

namespace piradio
{
  class RFDCService : public RFDCD::Service
  {
  };

  void handle_metal_msg(metal_log_level level,
			const char *format, ...)
  {
    va_list ap;

    va_start(ap, format);
    vprintf(format, ap);
    va_end(ap);
  }
  
  RFDCManager::RFDCManager() : _rfdc(nullptr)
  {
    struct metal_init_params init_param;

    init_param.log_handler = handle_metal_msg;
    init_param.log_level = METAL_LOG_ALERT;
        
    if (metal_init(&init_param)) {
      throw std::runtime_error("Failed to initialize libmetal");
    }
  }

  
  grpc::Service *RFDCManager::grpc_service()
  {
    return service;
  }
  
  void RFDCManager::attach_rfdc()
  {
    _rfdc = new RFDC();
  }

  void RFDCManager::startup_rfdc()
  {
  }

  void RFDCManager::shutdown_rfdc()
  {
  }
  
    
  RFDC *RFDCManager::rfdc()
  {
    return _rfdc;
  }  
}
