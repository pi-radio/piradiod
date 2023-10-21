#include <piradio/rfdc_dc.hpp>

void handle_metal_msg(metal_log_level level,
		      const char *format, ...)
{
  va_list ap;
  
  va_start(ap, format);
  vprintf(format, ap);
  va_end(ap);
}


int
main(int argc, char **argv)
{
  int i;
  struct metal_init_params init_param;
  
  init_param.log_handler = handle_metal_msg;
  init_param.log_level = METAL_LOG_ALERT;
  
  if (metal_init(&init_param)) {
    throw std::runtime_error("Failed to initialize libmetal");
  }

  piradio::RFDC *rfdc = new piradio::RFDC();

  //std::cout.setfill('0')
  
  for (i = 0; i < rfdc->n_adcs(); i++) {
    auto adc = rfdc->get_adc(i);

    std::cout << "ADC: " << i << std::endl;

    auto status = adc->block_status();

    std::cout << std::setfill('0');
    
    std::cout << " Sampling Rate: " << status.SamplingFreq << std::endl;

    std::cout << " Analog Data Path Status: 0x" << std::setw(4) << std::hex << status.AnalogDataPathStatus << std::dec << std::endl;
    std::cout << " Digital Data Path Status: 0x" << std::setw(4) << std::hex << status.DigitalDataPathStatus << std::dec << std::endl;
    std::cout << " Data Path Clocks: " << (status.DataPathClocksStatus ? "enabled" : "disabled") << std::endl;
    std::cout << " FIFO Flags Enabled: " << (status.IsFIFOFlagsEnabled ? "enabled" : "disabled") << std::endl;
    std::cout << " FIFO Flags Asserted: " << (status.IsFIFOFlagsAsserted ? "asserted" : "not asserted") << std::endl;

    std::cout << " Decimation factor: " << adc->decimation_factor() << std::endl;
  }

#if 0
  for (i = 0; i < rfdc->n_dacs(); i++) {
    auto dac = rfdc->get_dac(i);
    
    if (dac->enabled()) {
      dac->tune_NCO(f);
    }
  }
#endif
  
}
