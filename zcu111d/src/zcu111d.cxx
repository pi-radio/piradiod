#include <iostream>
#include <map>

#include <systemd/sd-daemon.h>

#include <sdbus-c++/sdbus-c++.h>

#include <piradio/rfdc.hpp>

piradio::RFDC *g_rfdc;

const std::string dbus_service_name = "io.pi-rad.zcu111d";
const std::string dbus_service_object = "/io/pi-rad/zcu111d/service";
const std::string dbus_fpga_object = "/io/pi-rad/zcu111d/fpga";


int main(int argc, char **argv)
{
  auto connection = sdbus::createSystemBusConnection(dbus_service_name);

  auto service_control = sdbus::createObject(*connection, dbus_service_object);
  auto fpga_control = sdbus::createObject(*connection, dbus_fpga_object);
  
  int Status;
  u16 Tile;
  u16 Block;
  //XRFdc_Config *ConfigPtr;
  //XRFdc *RFdcInstPtr = &RFdcInst;
  u32 ADCSetFabricRate[4];
  u32 DACSetFabricRate[4];
  u32 GetFabricRate;
  //XRFdc RFdcInst;
 
  struct metal_init_params init_param = METAL_INIT_DEFAULTS;

  if (metal_init(&init_param)) {
    printf("ERROR: Failed to run metal initialization\n");
    return XRFDC_FAILURE;
  }

  g_rfdc = new piradio::RFDC();
  
  return 0;
}
