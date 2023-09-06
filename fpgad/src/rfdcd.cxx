#include <iostream>
#include <map>

#include <piradio/daemon.hpp>
#include <piradio/services.hpp>
#include <piradio/rfdc.hpp>
#include <piradio/rfdc_tile.hpp>

using namespace piradio;

class rfdcd_daemon : public grpc_daemon
{
public:
  rfdcd_daemon() : grpc_daemon(services::rfdcd::bus)
  {
    auto obj = create_sdbus_object(services::rfdcd::root_object);
    auto iface = create_sdbus_iface(obj, services::rfdcd::root_interface);
    
    register_sdbus_method(iface, "get_n_adc_tiles", &rfdcd_daemon::get_n_adc_tiles);
    register_sdbus_method(iface, "get_n_dac_tiles", &rfdcd_daemon::get_n_dac_tiles);
    register_sdbus_method(iface, "get_reference_clock_freq", &rfdcd_daemon::get_reference_clock_freq);

    finalize_sdbus_object(obj);

    rfdc = new piradio::RFDC();
    
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

  int get_n_adc_tiles(void) {
    if (rfdc == nullptr) {
      return -1;
    }
    
    return rfdc->get_n_adc_tiles();
  }

  int get_n_dac_tiles(void) {
    if (rfdc == nullptr) {
      return -1;
    }
    
    return rfdc->get_n_adc_tiles();
  }
  
  double get_reference_clock_freq(int type, int no) {
    if (type != DCType::ADC && type != DCType::DAC) {
    }

    XRFdc_PLL_Settings s;

    if (type == DCType::ADC) {
      return 1000.0 * rfdc->get_adc_tile(no)->ref_clk_freq();
    } else if (type == DCType::DAC) {
      return 1000.0 * rfdc->get_dac_tile(no)->ref_clk_freq();      
    } else {
      throw std::runtime_error("Invalid data converter type");
    }
    
    return 0;
  }
  
  
private:
  piradio::RFDC *rfdc;
  //rfdcd rfdcd_service;  
};


int main(int argc, char **argv)
{
  struct metal_init_params init_param = METAL_INIT_DEFAULTS;

  if (metal_init(&init_param)) {
    printf("ERROR: Failed to run metal initialization\n");
    return XRFDC_FAILURE;
  }
  
  rfdcd_daemon d;

  d.start();

  return d.wait_on();
}
