#include <fmt/core.h>

#include <queue>
#include <iostream>

#include <piradio/cmdline.hpp>
#include <piradio/fpga.hpp>
#include <piradio/rfdc.hpp>
#include <piradio/rfdc_dc.hpp>
#include <piradio/zcu111.hpp>

piradio::ZCU111 zcu111;

extern std::map<piradio::frequency, std::vector<unsigned> > predefined;

int init()
{
  zcu111.program_reference();
  zcu111.program_Si5382();

  return 0;
}

int disable()
{
  std::cout << "Disabling LMX outputs" << std::endl;

  zcu111.mute_clocks();
  
  return 0;
}

int sample_freq(piradio::frequency f)
{
  std::cout << "Tuning sampling frequencies to " << f << std::endl;

  std::map<int, uint16_t> lmx_regs;
  piradio::LMX2594 lmx(zcu111.get_reference_frequency());

  lmx.tune(f, f);

  lmx.config.fill_regs(lmx_regs);

  zcu111.i2c_program_lmx(0xD, lmx_regs);
  
  //zcu111.tune_all(f);

  return 0;
}

int write_regs(piradio::frequency f)
{
  std::cout << "Writing regs for " << f << " reference: " << zcu111.get_reference_frequency() << std::endl;

  std::map<int, uint16_t> lmx_regs;
  piradio::LMX2594 lmx(zcu111.get_reference_frequency());

  lmx.tune(f, f);

  lmx.config.fill_regs(lmx_regs);

  std::ofstream regfile("regs-cpp.txt");
    
  for (auto it = lmx_regs.crbegin(); it != lmx_regs.crend(); it++) {
    uint8_t addr = it->first;
    uint16_t r = it->second;

    regfile << fmt::format("R{:d} 0x{:02x}{:04x}", int(addr), int(addr), r) <<  std::endl;
  }

  return 0;
}

int load_firmware(std::string fw_name)
{
  piradio::FPGA fpga;  

  std::filesystem::path bitfile(fw_name + ".bit.bin");
  std::filesystem::path overlay(fw_name + ".dtbo");

  if (!std::filesystem::exists(bitfile)) {
    std::cerr << "Bitstream '" << bitfile << "' not found" << std::endl;
    return 1;
  }

  if (!std::filesystem::exists(overlay)) {
    std::cerr << "Overlay '" << overlay << "' not found" << std::endl;
    return 1;
  }
  
  if (fpga.operating()) {
    std::cout << "Disabling RFDC and muting clockls" << std::endl;
    
    piradio::RFDC rfdc;
    
    rfdc.shutdown();

    zcu111.mute_clocks();
  }

  std::cout << "Loading firmware " << fw_name << std::endl;

  fpga.load_image(bitfile, overlay);

  // Note, we instantiate here to deal with it moving after bistream load
  piradio::RFDC rfdc;

  auto f = piradio::MHz(4096);

  std::cout << "Programming clocks" << std::endl;
  
  zcu111.tune_all(f);

  zcu111.enable_clocks();
  
  std::cout << "Starting RFDC" << std::endl;

  rfdc.reset();
  
  rfdc.startup();
  
  return 0;
}

int restart_rfdc()
{
  piradio::RFDC rfdc;

  rfdc.reset();

  rfdc.startup();

  return 0;
}

int rfdc_status()
{
  piradio::RFDC rfdc;

  auto status = rfdc.get_status();

  std::cout << "IP state: " << status.State << std::endl;

  for (int i = 0; i < rfdc.get_n_adc_tiles(); i++) {
    std::cout << "ADC Tile " << i << ":" << std::endl;

    
    std::cout << "  IsEnabled: " << fmt::format("{:08x}", status.ADCTileStatus[i].IsEnabled) <<  std::endl;
    std::cout << "  TileState: " << fmt::format("{:08x}", status.ADCTileStatus[i].TileState) <<  std::endl;
    std::cout << "  BlockStatusMask: " << fmt::format("{:02x}", status.ADCTileStatus[i].BlockStatusMask) <<  std::endl;
    std::cout << "  PowerUpState: " << fmt::format("{:08x}", status.ADCTileStatus[i].PowerUpState) <<  std::endl;
    std::cout << "  PLLState: " << fmt::format("{:08x}", status.ADCTileStatus[i].PLLState) <<  std::endl;

    auto tile = rfdc.get_adc_tile(i);
    
    std::cout << fmt::format("ISR {:08x}", tile->read32(0x200)) << std::endl;
    std::cout << fmt::format("IER {:08x}", tile->read32(0x204)) << std::endl;
    
    std::cout << fmt::format("I0S {:08x}", tile->read32(0x208)) << std::endl;
    std::cout << fmt::format("I0E {:08x}", tile->read32(0x20C)) << std::endl;

    std::cout << fmt::format("I1S {:08x}", tile->read32(0x210)) << std::endl;
    std::cout << fmt::format("I1E {:08x}", tile->read32(0x214)) << std::endl;

    std::cout << fmt::format("I2S {:08x}", tile->read32(0x218)) << std::endl;
    std::cout << fmt::format("I2E {:08x}", tile->read32(0x21C)) << std::endl;

    std::cout << fmt::format("I3S {:08x}", tile->read32(0x220)) << std::endl;
    std::cout << fmt::format("I3E {:08x}", tile->read32(0x224)) << std::endl;

    std::cout << fmt::format("CSTAT {:08x}", tile->read32(0x228)) << std::endl;
    std::cout << fmt::format("FIFO {:08x}", tile->read32(0x230)) << std::endl;
  }

  for (int i = 0; i < rfdc.get_n_dac_tiles(); i++) {
    std::cout << "DAC Tile " << i << ":" << std::endl;
    
    std::cout << "  IsEnabled: " << fmt::format("{:08x}", status.DACTileStatus[i].IsEnabled) <<  std::endl;
    std::cout << "  TileState: " << fmt::format("{:08x}", status.DACTileStatus[i].TileState) <<  std::endl;
    std::cout << "  BlockStatusMask: " << fmt::format("{:02x}", status.DACTileStatus[i].BlockStatusMask) <<  std::endl;
    std::cout << "  PowerUpState: " << fmt::format("{:08x}", status.DACTileStatus[i].PowerUpState) <<  std::endl;
    std::cout << "  PLLState: " << fmt::format("{:08x}", status.DACTileStatus[i].PLLState) <<  std::endl;

    auto tile = rfdc.get_dac_tile(i);
    
    std::cout << fmt::format("ISR {:08x}", tile->read32(0x200)) << std::endl;
    std::cout << fmt::format("IER {:08x}", tile->read32(0x204)) << std::endl;
    
    std::cout << fmt::format("I0S {:08x}", tile->read32(0x208)) << std::endl;
    std::cout << fmt::format("I0E {:08x}", tile->read32(0x20C)) << std::endl;

    tile->write32(0x208, tile->read32(0x208));

    std::cout << fmt::format("I1S {:08x}", tile->read32(0x210)) << std::endl;
    std::cout << fmt::format("I1E {:08x}", tile->read32(0x214)) << std::endl;

    std::cout << fmt::format("I2S {:08x}", tile->read32(0x218)) << std::endl;
    std::cout << fmt::format("I2E {:08x}", tile->read32(0x21C)) << std::endl;

    std::cout << fmt::format("I3S {:08x}", tile->read32(0x220)) << std::endl;
    std::cout << fmt::format("I3E {:08x}", tile->read32(0x224)) << std::endl;

    std::cout << fmt::format("CSTAT {:08x}", tile->read32(0x228)) << std::endl;
    std::cout << fmt::format("FIFO {:08x}", tile->read32(0x230)) << std::endl;
  }

  for (int i = 0; i < rfdc.n_adcs(); i++) {
    auto adc = rfdc.get_adc(i);
    auto adc_status = adc->block_status();

    std::cout << "ADC " << i << std::endl;

    std::cout << std::setfill('0');
    
    std::cout << " Sampling Rate: " << adc_status.SamplingFreq << std::endl;

    std::cout << " Analog Data Path Status: 0x" << std::setw(4) << std::hex << adc_status.AnalogDataPathStatus << std::dec << std::endl;
    std::cout << " Digital Data Path Status: 0x" << std::setw(4) << std::hex << adc_status.DigitalDataPathStatus << std::dec << std::endl;
    std::cout << " Data Path Clocks: " << (adc_status.DataPathClocksStatus ? "enabled" : "disabled") << std::endl;
    std::cout << " FIFO Flags Enabled: " << (adc_status.IsFIFOFlagsEnabled ? "enabled" : "disabled") << std::endl;
    std::cout << " FIFO Flags Asserted: " << (adc_status.IsFIFOFlagsAsserted ? "asserted" : "not asserted") << std::endl;

    std::cout << " Decimation factor: " << adc->decimation_factor() << std::endl;
  }

  for (int i = 0; i < rfdc.n_dacs(); i++) {
    auto dac = rfdc.get_dac(i);

    auto dac_status = dac->block_status();

    std::cout << "DAC " << i << std::endl;

    std::cout << std::setfill('0');
    std::cout << " Sampling Rate: " << dac_status.SamplingFreq << std::endl;

    std::cout << " Analog Data Path Status: 0x" << fmt::format("0x{:04x}", dac_status.AnalogDataPathStatus) << std::endl;
    std::cout << " Digital Data Path Status: 0x" << fmt::format("0x{:04x}", dac_status.DigitalDataPathStatus) << std::endl;
    std::cout << " Data Path Clocks: " << (dac_status.DataPathClocksStatus ? "enabled" : "disabled") << std::endl;
    std::cout << " FIFO Flags Enabled: " << (dac_status.IsFIFOFlagsEnabled ? "enabled" : "disabled") << std::endl;
    std::cout << " FIFO Flags Asserted: " << (dac_status.IsFIFOFlagsAsserted ? "asserted" : "not asserted") << std::endl;

    auto mixer = dac->get_mixer_settings();

    std::cout << " Mixer mode: " << mixer.MixerMode << std::endl;
  }
  
  return 0;
}

int mts_sync()
{
  piradio::RFDC rfdc;

  rfdc.MTSSync();

  return 0;
}

int bypass_mixer()
{
  piradio::RFDC rfdc;

  XRFdc_Mixer_Settings settings;

  for (int i = 0; i < rfdc.n_dacs(); i++) {
    auto dac = rfdc.get_dac(i);

    dac->bypass_mixer();
  }

  for (int i = 0; i < rfdc.get_n_dac_tiles(); i++) {
    auto dac_tile = rfdc.get_dac_tile(i);

    dac_tile->update_tile(XRFDC_EVENT_MIXER);
  }
  
  return 0;
}

int main(int argc, const char **argv)
{
  struct metal_init_params init_param = METAL_INIT_DEFAULTS;

  if (metal_init(&init_param)) {
    printf("ERROR: Failed to run metal initialization\n");
    return XRFDC_FAILURE;
  }

  piradio::CLI::CLI cli;

  cli.add_command("init", init);
  cli.add_command("sample-freq", sample_freq);
  cli.add_command("write-regs", write_regs);
  cli.add_command("load-firmware", load_firmware);
  cli.add_command("disable", disable);
  cli.add_command("rfdc-status", rfdc_status);
  cli.add_command("restart-rfdc", restart_rfdc);
  cli.add_command("mts-sync", mts_sync);
  cli.add_command("bypass-mixer", bypass_mixer);
  
  cli.parse(argc, argv);
}
