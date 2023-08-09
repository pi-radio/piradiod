#include <iostream>
#include <map>

#include <grpc/grpc.h>
#include <grpcpp/security/server_credentials.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>

#include "zcu111.grpc.pb.h"

#include <piradio/daemon.hpp>
#include <piradio/services.hpp>
#include <piradio/lmx2594.hpp>
#include <piradio/i2c.hpp>
#include <piradio/clocks.hpp>


using namespace piradio;

class zcu111d final : public ZCU111::Service
{
public:
  zcu111d();

  virtual grpc::Status GetClockConfig(grpc::ServerContext* context, const ::google::protobuf::Empty* request, ::ClockConfig* response);
  virtual grpc::Status SetClockConfig(grpc::ServerContext* context, const ::ClockConfig* request, ::google::protobuf::Empty* response);

  
  
protected:
  LMX2594 zcu111_lmx;
  zcu111_i2c i2c_si5382;
  zcu111_i2c i2c_spi;
};

zcu111d::zcu111d() :
  i2c_si5382(zcu111_i2c::find_device(0x68), 0x68),
  i2c_spi(zcu111_i2c::find_device(0x2F), 0x2F),
  zcu111_lmx(MHz(122.88))
{
}

grpc::Status zcu111d::GetClockConfig(grpc::ServerContext* context, const ::google::protobuf::Empty* request, ::ClockConfig* response)
{
  try {
  } catch(...) {
    return grpc::Status(grpc::StatusCode::INTERNAL, "Failed to get clock config");
  }
    
    
  return grpc::Status::OK;
}

grpc::Status zcu111d::SetClockConfig(grpc::ServerContext* context, const ::ClockConfig* request, ::google::protobuf::Empty* response)
{
  try {
  } catch(...) {
    return grpc::Status(grpc::StatusCode::INTERNAL, "Failed to set clock config");
  }    
  
  return grpc::Status::OK;
}

const std::string zcu111_obj = "/io/piradio/zcu111d/zcu111";
const std::string zcu111_iface = "io.piradio.zcu111d.zcu111";

class zcu111d_daemon : public grpc_daemon
{
public:
  zcu111d_daemon() : grpc_daemon(piradio::services::zcu111d::bus)
  {
    setup_clocks();

    auto obj = create_sdbus_object(piradio::services::zcu111d::root_object);

    auto iface = create_sdbus_iface(obj, piradio::services::zcu111d::root_interface);
    
    register_sdbus_method(iface, "enable_dc_clock", &zcu111d_daemon::enable_dc_clock);
    register_sdbus_method(iface, "set_clock_rate", &zcu111d_daemon::set_clock_rate);

    finalize_sdbus_object(obj);
    
    bind_addresses.push_back("0.0.0.0:7779");
    grpc_services.push_back(&zcu111d_service);
  }

  virtual int prepare(void) {
    return 0;
  }
  
  void enable_dc_clock(bool b) {
  }
  
  void set_clock_rate(double d) {
    std::cout << "set_clock_rate: " << d << std::endl;
    
  }
  
private:
  zcu111d zcu111d_service;  
};


int main(int argc, char **argv)
{
  zcu111d_daemon d;

  d.start();

  return d.wait_on();
}

