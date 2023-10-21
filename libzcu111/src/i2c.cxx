#include <iostream>
#include <fstream>
#include <atomic>
#include <filesystem>
#include <initializer_list>
#include <vector>
#include <cctype>
#include <fmt/core.h>

#include <unistd.h>

#include <piradio/i2c.hpp>

#include <sys/ioctl.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>

extern "C" {
#include <i2c/smbus.h>
}

namespace fs = std::filesystem;

namespace piradio
{
  int zcu111_i2c::find_LMXs()
  {
    int retval = -1;

    fs::path i2c_dev_path("/sys/bus/i2c/devices");

    for (auto const &de: fs::directory_iterator(i2c_dev_path)) {
      auto fn = de.path().filename().string();

      if (fn.find("i2c-") != 0)
	continue;

      int bus_no = std::stoi(fn.substr(4));
      
      for (auto const &de2: fs::directory_iterator(de.path())) {
	std::string fn2 = de2.path().filename().string();

	if(!std::isdigit(fn2[0]) || std::stoi(fn2) != bus_no) {
	  continue;
	}

	std::ifstream inf(de2/fs::path("name"));

	std::string l;

	std::getline(inf, l);

	if (l.find("sc18is60") == 0) {
	  return bus_no;
	}
      }
    }

    throw std::runtime_error("Could not find LMX bus");
  }

  
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
	  continue;
	}

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
    
  int zcu111_i2c::read(uint8_t cmd, uint8_t *buf)
  {
    return i2c_smbus_read_block_data(fd, cmd, buf);
  }

  void zcu111_i2c::write(uint8_t cmd, int retries)
  {
    int retval = 0;

    do {
      retval = i2c_smbus_write_byte(fd, cmd);

      if (retval < 0) {
	std::cout << "Write byte fail" << std::endl;
	usleep(1000);
      }
    } while(retval < 0 && retries--);

    if (retval) {
      throw std::runtime_error("Failed to write to i2c bus");
    }
  }
    
  void zcu111_i2c::write(uint8_t addr, uint8_t data, int retries)
  {
    int retval = 0;

    do {
      retval = i2c_smbus_write_byte_data(fd, addr, data);

      if (retval < 0) {
	std::cout << "Write byte data fail" << std::endl;
	usleep(1000);
      }
    } while(retval < 0 && retries--);

    if (retval) {
      throw std::runtime_error("Failed to write to i2c bus");
    }
  }

  void zcu111_i2c::write(uint8_t cmd, std::initializer_list<uint8_t> il, int retries)
  {
    int retval = 0;

    do {
      retval = i2c_smbus_write_i2c_block_data(fd, cmd, il.size(), std::data(il));

      if (retval < 0) {
	std::cout << "Write block fail" << std::endl;
	usleep(1000);
      }
    } while(retval < 0 && retries--);

    if (retval) {
      throw std::runtime_error("Failed to write to i2c bus");
    }
  }    

  void zcu111_i2c::write(std::initializer_list<uint8_t> il, int retries)
  {
    int result;

    do {
      result = ::write(fd, std::data(il), il.size());
    } while (result != il.size() && retries--);

    if (result != il.size()) {
      throw std::runtime_error("Failed to write to i2c bus");
    }    
  }

  void zcu111_i2c::txn(uint16_t addr, std::initializer_list<uint8_t> il, int retries)
  {
    int result;
    uint8_t buf[32];
    struct i2c_msg msg;
    struct i2c_rdwr_ioctl_data xfer;
    
    do {
      memcpy(buf, std::data(il), il.size());

      msg.addr = addr;
      msg.flags = 0;
      msg.len = il.size();
      msg.buf = (__u8 *)buf;

      xfer.nmsgs = 1;
      xfer.msgs = &msg;

      result = ioctl(fd, I2C_RDWR, &xfer);
    } while (result < 0 && --retries);

    if (result < 0) {
      std::cerr << "I2C txn failure " << std::strerror(errno) << std::endl;
      throw std::runtime_error("I2C txn failed");
    }
  }
}
