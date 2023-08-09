#include <iostream>
#include <map>

#include <piradio/daemon.hpp>
#include <piradio/services.hpp>
#include <piradio/rfdc.hpp>

using namespace piradio;

class rfdcd_daemon : public grpc_daemon
{
public:
  rfdcd_daemon() : grpc_daemon(services::rfdcd::bus)
  {
    auto obj = create_sdbus_object(services::rfdcd::root_object);
    auto iface = create_sdbus_iface(obj, services::rfdcd::root_interface);
    
    register_sdbus_method(iface, "get_reference_clock_freq", &rfdcd_daemon::get_reference_clock_freq);

    finalize_sdbus_object(obj);
    
    //bind_addresses.push_back("0.0.0.0:7779");
    //grpc_services.push_back(&rfdcd_service);
  }

  virtual int prepare(void) {
    return 0;
  }

  void prepare_for_firmware_unload(void) {
  }

  void firmware_loaded(void) {
  }
  
  double get_reference_clock_freq(int type, int no) {
    return 0;
  }
  
  
private:
  piradio::RFDC rfdc;
  //rfdcd rfdcd_service;  
};


int main(int argc, char **argv)
{
  rfdcd_daemon d;

  d.start();

  return d.wait_on();
}
