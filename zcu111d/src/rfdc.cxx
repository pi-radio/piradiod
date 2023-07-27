#include <iostream>
#include <atomic>
#include <filesystem>
#include <initializer_list>
#include <vector>
#include <fmt/core.h>

#include <piradio/rfdc.hpp>
#include <piradio/rfdc_dc.hpp>

#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#define XIIC_BLOCK_MAX	16	/* Max data length */
#define I2C_SMBUS_WRITE	0
#define I2C_SMBUS_I2C_BLOCK  6

namespace fs = std::filesystem;

namespace piradio
{
  class zcu111_i2c
  {
    int fd;
    fs::path dev_path;
    
  public:
    zcu111_i2c(int n) : dev_path(fmt::format("/dev/i2c-{:d}", n))
    {
      int result;
      
      fd = open(dev_path.c_str(), O_RDWR);

      result = ioctl(fd, I2C_SLAVE_FORCE, 0x2F);

      if (result != 0) {
	throw std::runtime_error("I2C error");
      }
    }

    void write(uint8_t cmd, std::initializer_list<uint8_t> il)
    {
	struct i2c_smbus_ioctl_data args;
	unsigned char b[17];

	int i = 1;

	for (uint8_t x : il) {
	  b[i++] = x;
	}

	b[0] = i - 1;

	args.read_write = I2C_SMBUS_WRITE;
	args.command = cmd;
	args.size = I2C_SMBUS_I2C_BLOCK;
	args.data = (i2c_smbus_data *)&b;
	
	ioctl(fd, I2C_SMBUS, &args);
    }
    
    void write(uint8_t cmd, const uint8_t *val, uint8_t len)
    {
	struct i2c_smbus_ioctl_data args;
	unsigned char b[17];

	assert(len <= 16);
	
	b[0] = len;
	memcpy(&b[1], val, len);

	args.read_write = I2C_SMBUS_WRITE;
	args.command = cmd;
	args.size = I2C_SMBUS_I2C_BLOCK;
	args.data = (i2c_smbus_data *)&b;
	
	ioctl(fd, I2C_SMBUS, &args);
    }
  };

  void program_LMX2594(zcu111_i2c &i2c, std::vector<unsigned int> &regs)
  {
    std::cout << "Programming LMX" << std::endl;
    
    i2c.write(0xD, { 0, 0, 2 });
    usleep(1000);

    i2c.write(0xD, { 0, 0, 0 });
    usleep(1000);

    for (auto r : regs) {
      i2c.write(0xD, { (uint8_t)(r >> 16), (uint8_t)(r >> 8), (uint8_t)r });
      usleep(1000);
    }
    
    usleep(10000);
    /* FCAL_EN = 1 ???? */
    auto r = regs.back() | 0x10;
    //i2c.write(0xD, { (uint8_t)(r >> 16), (uint8_t)(r >> 8), (uint8_t)r });

    i2c.write(0xD, { 0, 0, 1 });
    usleep(1000);

  }

  void program_LMK04208(zcu111_i2c &i2c, std::vector<unsigned int> &regs)
  {
    for (auto r : regs) {
      i2c.write(0x2, { (uint8_t)(r >> 24), (uint8_t)(r >> 16), (uint8_t)(r >> 8), (uint8_t)r });
      usleep(1000);
    }
  }

  
  RFDC::RFDC()
  {
    int result;
    int tile, block, n;

    zcu111_i2c i2c(12);
    
    std::vector<unsigned int> LMK04208_regs = {
      {0x00160040,0x80140320,0x80140321,0x80140322,
       0xC0140023,0x40140024,0x80141E05,0x03300006,0x01300007,0x06010008,
       0x55555549,0x9102410A,0x0401100B,0x1B0C006C,0x2302886D,0x0200000E,
       0x8000800F,0xC1550410,0x00000058,0x02C9C419,0x8FA8001A,0x10001E1B,
       0x0021201C,0x0180033D,0x0200033E,0x003F001F
      }
    };
    
    std::vector<unsigned int> LMX_regs_4GHz = {
      0x700000, 0x6f0000, 0x6e0000, 0x6d0000, 0x6c0000, 0x6b0000, 0x6a0000,
      0x690021, 0x680000, 0x670000, 0x663f80, 0x650011, 0x640000, 0x630000,
      0x620200, 0x610888, 0x600000, 0x5f0000, 0x5e0000, 0x5d0000, 0x5c0000,
      0x5b0000, 0x5a0000, 0x590000, 0x580000, 0x570000, 0x560000, 0x55d300,
      0x540001, 0x530000, 0x521e00, 0x510000, 0x506666, 0x4f0026, 0x4e0003,
      0x4d0000, 0x4c000c, 0x4b0800, 0x4a0000, 0x49003f, 0x480001, 0x470081,
      0x46c350, 0x450000, 0x4403e8, 0x430000, 0x4201f4, 0x410000, 0x401388,
      0x3f0000, 0x3e0322, 0x3d00a8, 0x3c0000, 0x3b0001, 0x3a8001, 0x390020,
      0x380000, 0x370000, 0x360000, 0x350000, 0x340820, 0x330080, 0x320000,
      0x314180, 0x300300, 0x2f0300, 0x2e07fc, 0x2dc0cc, 0x2c0c23, 0x2b0005,
      0x2a0000, 0x290000, 0x280000, 0x270030, 0x260000, 0x250304, 0x240041,
      0x230004, 0x220000, 0x211e21, 0x200393, 0x1f03ec, 0x1e318c, 0x1d318c,
      0x1c0488, 0x1b0002, 0x1a0db0, 0x190624, 0x18071a, 0x17007c, 0x160001,
      0x150401, 0x14e048, 0x1327b7, 0x120064, 0x11012c, 0x100080, 0x0f064f,
      0x0e1e70, 0x0d4000, 0x0c5001, 0x0b0018, 0x0a10d8, 0x090604, 0x082000,
      0x0740b2, 0x06c802, 0x0500c8, 0x040a43, 0x030642, 0x020500, 0x010808,
      0x00248c
    };
    
    program_LMK04208(i2c, LMK04208_regs);
    program_LMX2594(i2c, LMX_regs_4GHz);
    
    cfg = XRFdc_LookupConfig(0);

    if (cfg == NULL) {
      throw std::runtime_error("Unable to find config");
    }
  
    result = XRFdc_RegisterMetal(&rfdc, 0, &metal_dev);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to open rfdc metal device");
    }

    result = XRFdc_CfgInitialize(&rfdc, cfg);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to initialize rfdc");
    }

    
    result = XRFdc_GetIPStatus(&rfdc, &ip_status);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to get IP status");     
    }
    
    n = 0;

    std::cout << "Setting up ADCs..." << std::endl;
    
    for (tile = 0; tile < 4; tile++) {
      if (!ip_status.ADCTileStatus[tile].IsEnabled) {
	continue;
      }    

      std::cout << "ADC Tile " << tile << std::endl;
      
      adc_tiles[tile] = new ADCTile(*this, tile);

      adc_tiles[tile]->reset();

      if (!adc_tiles[tile]->pll_locked()) {
	std::cerr << adc_tiles[tile]->get_id_string() << ": PLL not locked" << std::endl;
      }

      for (block = 0; block < 4; block++) {
	if (!(ip_status.ADCTileStatus[tile].BlockStatusMask & (1 << block))) {
	  continue;
	}
	std::cout << " Block " << block << std::endl;

	adcs[n] = new ADC(*adc_tiles[tile], block);

	adcs[n]->tune_NCO(1.25e9);

	adcs[n]->set_mixer_passthrough();
	
	n++;
      }
    }


    std::cout << "Setting up DACs..." << std::endl;
    
    for (tile = 0; tile < 4; tile++) {
      if (!ip_status.DACTileStatus[tile].IsEnabled) {
	continue;
      }

      std::cout << "DAC Tile " << tile << std::endl;

      dac_tiles[tile] = new DACTile(*this, tile);

      dac_tiles[tile]->reset();

      if (!dac_tiles[tile]->pll_locked()) {
	std::cerr << dac_tiles[tile]->get_id_string() << ": PLL not locked" << std::endl;
      }

      for (block = 0; block < 4; block++) {
	if (!(ip_status.DACTileStatus[tile].BlockStatusMask & (1 << block))) {
	  continue;
	}
	std::cout << " Block " << block << std::endl;

	if (true) {
	  XRFdc_Mixer_Settings settings;
	  
	  settings.Freq = 1250.0;
	  settings.PhaseOffset = 0;
	  settings.EventSource = XRFDC_EVNT_SRC_TILE;
	  settings.CoarseMixFreq = XRFDC_COARSE_MIX_BYPASS;
	  settings.MixerMode = XRFDC_MIXER_MODE_C2R;
	  settings.FineMixerScale = XRFDC_MIXER_SCALE_1P0;
	  settings.MixerType = XRFDC_MIXER_TYPE_FINE;
	  
	  XRFdc_SetMixerSettings(&rfdc, XRFDC_DAC_TILE, tile, block, &settings);
	}
	  
	dacs[n] = new DAC(*dac_tiles[tile], block);


	
	//dacs[n]->tune_NCO(1.25e9);
	
	n++;
      }
    }

    
    for (auto adc : adcs) {
      //std::get<1>(adc)->set_mixer_passthrough();
      std::get<1>(adc)->tune_NCO(1.25e9);
    }
  

    for (auto adc : adcs) {
      std::get<1>(adc)->dump();
    }
    
  }

  int RFDC::reset()
  {
  }

  int RFDC::load_config()
  {
    int result;
    XRFdc_Config *cfg;
    cfg = XRFdc_LookupConfig(0);

    if (cfg == NULL) {
      throw std::runtime_error("Unable to find config");
    }

    XRFdc rfdc;
    struct metal_device *metal_dev;

    result = XRFdc_RegisterMetal(&rfdc, 0, &metal_dev);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to open rfdc metal device");
    }

    
    result = XRFdc_CfgInitialize(&rfdc, cfg);

    if (result != XRFDC_SUCCESS) {
      throw std::runtime_error("Unable to initialize rfdc");
    }
  }
  
};
