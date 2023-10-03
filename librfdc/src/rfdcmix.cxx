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
  struct metal_init_params init_param;
  
  init_param.log_handler = handle_metal_msg;
  init_param.log_level = METAL_LOG_ALERT;
  
  if (metal_init(&init_param)) {
    throw std::runtime_error("Failed to initialize libmetal");
  }

  piradio::RFDC *rfdc = new piradio::RFDC();

  int i;
  
  for (i = 0; i < rfdc->n_adcs(); i++) {
    auto adc = rfdc->get_adc(i);

    std::cout << "ADC " << i << std::endl; 
    std::cout << " Enabled: " << adc->enabled() << std::endl;
    
    if (adc->enabled()) {
      //adc->tune_NCO(f);
    }
  }
  
  for (i = 0; i < rfdc->n_dacs(); i++) {
    auto dac = rfdc->get_dac(i);

    std::cout << "DAC " << i << std::endl;
    std::cout << " Enabled: " << dac->enabled() << std::endl;
    
    if (dac->enabled()) {
      //dac->tune_NCO(f);
    }
  }
}
