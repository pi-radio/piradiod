#include <iostream>
#include <cstring>

#include <signal.h>

#include <piradio/daemon.hpp>

namespace piradio
{
  grpc_daemon::grpc_daemon(const std::string &_service_name) : daemon(_service_name)
  {
    std::cout << "grpc_daemon" << std::endl;
  }

  void grpc_daemon::launch(void)
  {
    build_grpc_services();
    
    daemon::launch();
  }
  
  void grpc_daemon::build_grpc_services(void)
  {
    grpc::reflection::InitProtoReflectionServerBuilderPlugin();
 
    grpc::ServerBuilder builder;

    for (auto addr : bind_addresses) {
      builder.AddListeningPort(addr, grpc::InsecureServerCredentials());
    }
    
    for (auto service: grpc_services) {
      builder.RegisterService(service);
    }
    
    grpc_server = builder.BuildAndStart();
  }
}
