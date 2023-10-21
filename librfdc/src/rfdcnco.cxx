#include <piradio/cmdline.hpp>
#include <piradio/frequency.hpp>
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
get_ref_clk_frequency()
{
  int i;
  piradio::RFDC *rfdc = new piradio::RFDC();

  for (i = 0; i < rfdc->n_adcs(); i++) {
    auto adc = rfdc->get_adc(i);

    if (adc->enabled()) {
      std::cout << "ADC " << i << ": " << adc->ref_clk_freq() << std::endl;
    }
  }
  
  for (i = 0; i < rfdc->n_dacs(); i++) {
    auto dac = rfdc->get_dac(i);
    
    if (dac->enabled()) {
      std::cout << "DAC " << i << ": " << dac->ref_clk_freq() << std::endl;
    }
  }

  return 0;
}

int
get_sample_frequency()
{
  int i;
  piradio::RFDC *rfdc = new piradio::RFDC();

  for (i = 0; i < rfdc->n_adcs(); i++) {
    auto adc = rfdc->get_adc(i);

    if (adc->enabled()) {
      std::cout << "ADC " << i << ": " << adc->sample_freq() << std::endl;
    }
  }
  
  for (i = 0; i < rfdc->n_dacs(); i++) {
    auto dac = rfdc->get_dac(i);
    
    if (dac->enabled()) {
      std::cout << "DAC " << i << ": " << dac->sample_freq() << std::endl;
    }
  }

  return 0;
}

int
get_nco_frequency()
{
  int i;
  piradio::RFDC *rfdc = new piradio::RFDC();

  for (i = 0; i < rfdc->n_adcs(); i++) {
    auto adc = rfdc->get_adc(i);

    std::cout << "ADC " << i << ": ";

    if (adc->enabled()) {
      std::cout << adc->NCO_freq();
    } else {
      std::cout << "disabled";
    }
    
    std::cout << std::endl;
  }
  
  for (i = 0; i < rfdc->n_dacs(); i++) {
    auto dac = rfdc->get_dac(i);
    
    std::cout << "DAC " << i << ": ";

    if (dac->enabled()) {
      std::cout << dac->NCO_freq();
    } else {
      std::cout << "disabled";
    }
    
    std::cout << std::endl;
  }

  return 0;
}

int
set_nco_frequency(piradio::frequency f)
{
  int i;
  piradio::RFDC *rfdc = new piradio::RFDC();

  for (i = 0; i < rfdc->n_adcs(); i++) {
    auto adc = rfdc->get_adc(i);

    if (adc->enabled()) {
      adc->tune_NCO(f.Hz());
    }
  }
  
  for (i = 0; i < rfdc->n_dacs(); i++) {
    auto dac = rfdc->get_dac(i);
    
    if (dac->enabled()) {
      dac->tune_NCO(f.Hz());
    }
  }

  return 0;
}

int
set_fs2(void)
{
  int i;
  piradio::RFDC *rfdc = new piradio::RFDC();

  for (i = 0; i < rfdc->n_adcs(); i++) {
    auto adc = rfdc->get_adc(i);

    if (adc->enabled()) {
      adc->set_fs2();
    }
  }
  
  for (i = 0; i < rfdc->n_dacs(); i++) {
    auto dac = rfdc->get_dac(i);
    
    if (dac->enabled()) {
      dac->set_fs2();
    }
  }

  return 0;
}

int
set_fs4(void)
{
  int i;
  piradio::RFDC *rfdc = new piradio::RFDC();

  for (i = 0; i < rfdc->n_adcs(); i++) {
    auto adc = rfdc->get_adc(i);

    if (adc->enabled()) {
      adc->set_fs4();
    }
  }
  
  for (i = 0; i < rfdc->n_dacs(); i++) {
    auto dac = rfdc->get_dac(i);
    
    if (dac->enabled()) {
      dac->set_fs4();
    }
  }

  return 0;
}

int
set_neg_fs4(void)
{
  int i;
  piradio::RFDC *rfdc = new piradio::RFDC();

  for (i = 0; i < rfdc->n_adcs(); i++) {
    auto adc = rfdc->get_adc(i);

    if (adc->enabled()) {
      adc->set_neg_fs4();
    }
  }
  
  for (i = 0; i < rfdc->n_dacs(); i++) {
    auto dac = rfdc->get_dac(i);
    
    if (dac->enabled()) {
      dac->set_neg_fs4();
    }
  }

  return 0;
}


int
main(int argc, const char **argv)
{
  struct metal_init_params init_param;
  
  init_param.log_handler = handle_metal_msg;
  init_param.log_level = METAL_LOG_ALERT;
  
  if (metal_init(&init_param)) {
    throw std::runtime_error("Failed to initialize libmetal");
  }

  piradio::CLI::CLI cli;

  cli.add_command("get", get_nco_frequency);
  cli.add_command("get-sample-freq", get_sample_frequency);
  cli.add_command("get-ref-clk", get_ref_clk_frequency);
  cli.add_command("set", set_nco_frequency);
  cli.add_command("fs/2", set_fs2);
  cli.add_command("fs/4", set_fs4);
  cli.add_command("-fs/4", set_neg_fs4);
  
  cli.parse(argc, argv);
}
