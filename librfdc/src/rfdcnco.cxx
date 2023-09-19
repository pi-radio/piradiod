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
  double f = strtod(argv[1], NULL);
  
  for (i = 0; i < 8; i++) {
    rfdc->get_adc(i)->tune_NCO(f);
  }
  
  for (i = 0; i < 8; i++) {
    rfdc->get_dac(i)->tune_NCO(f);
  }
}
