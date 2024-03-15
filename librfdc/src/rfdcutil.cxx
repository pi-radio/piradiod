#include <queue>
#include <iostream>

#include <piradio/cmdline.hpp>

#include <piradio/rfdc_dc.hpp>

void handle_metal_msg(metal_log_level level,
		      const char *format, ...)
{
  va_list ap;
  
  va_start(ap, format);
  vprintf(format, ap);
  va_end(ap);
}

int status()
{
  return 0;
}

int disable_invsinc(piradio::CLI::args_t &args)
{
  piradio::RFDC *rfdc = new piradio::RFDC();

  auto dac_no = args.front();
  
  if (dac_no == "all") {
    for (int i = 0; i < rfdc->n_dacs(); i++) {
      auto dac = rfdc->get_dac(i);

      std::cout << "Setting mode for dac " << i << std::endl;
      
      dac->set_inv_sinc_mode(0);
    }
    
  } else {
    int n = std::stoi(dac_no);
    
    rfdc->get_dac(n)->set_inv_sinc_mode(0);
  }
  
  return 0;
}

int enable_invsinc(piradio::CLI::args_t &args)
{
  piradio::RFDC *rfdc = new piradio::RFDC();

  auto dac_no = args.front();
  
  if (dac_no == "all") {
    for (int i = 0; i < rfdc->n_dacs(); i++) {
      auto dac = rfdc->get_dac(i);

      std::cout << "Setting mode for dac " << i << std::endl;
      
      dac->set_inv_sinc_mode(1);
    }
    
  } else {
    int n = std::stoi(dac_no);
    
    rfdc->get_dac(n)->set_inv_sinc_mode(1);
  }
  
  return 0;
}



int main(int argc, const char **argv)
{
  piradio::CLI::CLI cli;

  int i;
  struct metal_init_params init_param;
  
  init_param.log_handler = handle_metal_msg;
  init_param.log_level = METAL_LOG_ALERT;
  
  if (metal_init(&init_param)) {
    throw std::runtime_error("Failed to initialize libmetal");
  }


  
  cli.add_command("status", status);
  cli.add_command("enable-invsinc", enable_invsinc);
  cli.add_command("disable-invsinc", disable_invsinc);

  cli.parse(argc, argv);
}
