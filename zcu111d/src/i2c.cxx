#include <iostream>
#include <atomic>
#include <filesystem>
#include <initializer_list>
#include <vector>
#include <fmt/core.h>

#include <piradio/rfdc.hpp>
#include <piradio/rfdc_dc.hpp>

#include <piradio/i2c.hpp>

#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

extern "C" {
#include <i2c/smbus.h>
}

namespace fs = std::filesystem;

namespace piradio
{  
  int zcu111_i2c::find_device(uint8_t addr)
  {
    int retval = -1;
    
    fs::path dev_path = fs::path("/dev");
    
    for (auto const &de: fs::directory_iterator(dev_path)) {
      char buf[34];
      uint8_t len;
      buf[0] = 16;
      auto fn = de.path().filename().string(); 
      if(fn.find("i2c-") == 0) {
	int devno = std::stol(fn.substr(4));
	  
	zcu111_i2c i2c(devno, addr);
	  
	memset(buf, 0, sizeof(buf));

	if (i2c.read() < 0) {
	  std::cout << "Skipping " << de.path() << ": " << std::strerror(errno) << std::endl;
	  continue;
	}

	std::cout << "Found " << de.path() << ": " << buf << std::endl;

	retval = devno;
      }
    }

    return retval;
  }
    
  zcu111_i2c::zcu111_i2c(int n, uint8_t addr) : dev_path(fmt::format("/dev/i2c-{:d}", n))
  {
    int result;
      
    fd = open(dev_path.c_str(), O_RDWR);

    result = ioctl(fd, I2C_SLAVE_FORCE, addr);

    if (result != 0) {
      throw std::runtime_error("I2C error");
    }
  }


  int zcu111_i2c::read(void)
  {
    return i2c_smbus_read_byte(fd);
  }

  uint8_t zcu111_i2c::read(uint8_t cmd)
  {
    return (uint8_t)i2c_smbus_read_byte_data(fd, cmd);
  }
    
  int zcu111_i2c::read(uint8_t cmd, uint8_t *len, uint8_t *buf)
  {
    return i2c_smbus_read_block_data(fd, cmd, buf);
  }

  int zcu111_i2c::write(uint8_t cmd)
  {
    return i2c_smbus_write_byte(fd, cmd);
  }
    
  int zcu111_i2c::write(uint8_t addr, uint8_t data)
  {
    return i2c_smbus_write_byte_data(fd, addr, data);
  }


  int zcu111_i2c::write(uint8_t cmd, std::initializer_list<uint8_t> il)
  {
    return i2c_smbus_write_i2c_block_data(fd, cmd, il.size(), std::data(il));
  }    

}
